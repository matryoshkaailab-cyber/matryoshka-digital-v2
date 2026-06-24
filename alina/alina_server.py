#!/usr/bin/env python3.12
"""
alina_server.py — HTTP API для Алины на :8470.

ARCHITECTURE v3.0:
  /chat, /think, /task → вызывает HERMES AGENT (subprocess) с полным toolset
  /health → статус

TOOLS доступные через API (всё что у gateway):
  - browser (парсинг сайтов)
  - search (web search)
  - memory (MEMORY.md, fact_store)
  - session_search (история)
  - vision (анализ фото)
  - image_gen (генерация)
  - tts (голос)
  - todo (задачи)
  - terminal (SSH)
  - skill_manage (скиллы)

HERMES AGENT запускается через `hermes agent run --profile alina --message "..."` (неинтерактивный режим)
"""
import os, json, time, uuid, base64, subprocess, shlex
import urllib.request, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

PORT = 8470
ALINA_HOME = "/root/.hermes/profiles/alina"
LOG_FILE = "/var/log/alina_server.log"
ALINA_TASKS = Path("/root/matryoshka/alina_tasks")
ALINA_TASKS.mkdir(parents=True, exist_ok=True)

# Загружаем .env
ENV = {}
env_file = f"{ALINA_HOME}/.env"
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                ENV[k.strip()] = v.strip()

# Auth (постоянный UUID из .env)
AUTH_USER = ENV.get("ALINA_API_USER", "alina")
AUTH_PASS = ENV.get("ALINA_API_UUID") or uuid.uuid4().hex
if not ENV.get("ALINA_API_UUID"):
    with open(env_file, "a") as f:
        f.write(f"\nALINA_API_UUID={AUTH_PASS}\n")
    os.chmod(env_file, 0o600)

MINIMAX_BASE = ENV.get("MINIMAX_BASE_URL", "https://api.minimax.io/v1")
HERMES_BIN = "/usr/local/lib/hermes-agent/venv/bin/hermes"

# Модели — для /health и fallback (простой режим без tools)
MODELS = {
    "minimax-m3": {"url": f"{MINIMAX_BASE}/chat/completions", "model": "MiniMax-M3", "key_env": "MINIMAX_API_KEY"},
    "minimax-m2.7": {"url": f"{MINIMAX_BASE}/chat/completions", "model": "MiniMax-M2.7", "key_env": "MINIMAX_API_KEY"},
    "gemini-flash": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "google/gemini-2.5-flash", "key_env": "OPENROUTER_API_KEY"},
    "claude-haiku": {"url": "https://openrouter.ai/api/v1/chat/completions", "model": "anthropic/claude-3-haiku", "key_env": "OPENROUTER_API_KEY"},
    "qwen-local": {"url": "http://127.0.0.1:8765/v1/chat/completions", "model": "qwen3.7-plus", "key_env": None},
}
FALLBACK_ORDER = ["gemini-flash", "claude-haiku", "minimax-m2.7", "minimax-m3", "qwen-local"]


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


# === HERMES AGENT MODE (with tools) ===

def ask_hermes_agent(message, system=None, max_turns=10, timeout=180):
    """
    Запускает Hermes Agent в неинтерактивном режиме через `hermes chat`.
    Алина получает ВСЕ tools (browser, search, memory, terminal, и т.д.)
    SOUL.md добавляется в system prompt.

    Returns: dict {ok, text, model, tools_used, duration}
    """
    # Загружаем SOUL.md
    soul_path = f"{ALINA_HOME}/SOUL.md"
    try:
        soul = open(soul_path).read()[:4000]
    except:
        soul = "Ты — Алина, тёплый личный ассистент Николая."

    # system = SOUL.md + (опционально override от caller)
    effective_system = soul
    if system:
        effective_system = f"{soul}\n\n---\n\n{system}"

    # prepend system context к сообщению (т.к. --system не поддерживается)
    final_message = f"[SYSTEM INSTRUCTIONS — СТРОГО СОБЛЮДАТЬ]\n{effective_system}\n\n[END SYSTEM]\n\nТеперь ответь на:\n\n{message}"

    cmd = [
        HERMES_BIN, "chat",
        "-q", final_message,
        "-Q",
        "--max-turns", str(max_turns),
        "--profile", "alina",  # КРИТИЧНО: загружает SOUL.md Алины, не HERMES
    ]

    env = os.environ.copy()
    env["HERMES_HOME"] = "/root/.hermes"
    env["HERMES_PROFILE"] = "alina"
    env["ALINA_TASKS"] = str(ALINA_TASKS)

    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd="/root"
        )
        duration = time.time() - t0

        if result.returncode == 0 and result.stdout.strip():
            return {
                "ok": True,
                "text": result.stdout.strip(),
                "model": "hermes-agent",
                "duration": duration,
                "mode": "tools",
                "tools_available": ["browser", "search", "memory", "session_search", "vision", "image_gen", "tts", "todo", "terminal", "skill_manage"],
            }
        else:
            log(f"hermes-agent failed: rc={result.returncode}, stderr={result.stderr[:200]}")
            return {
                "ok": False,
                "error": f"hermes-agent exit {result.returncode}",
                "stderr": result.stderr[:500] if result.stderr else "",
                "duration": duration,
            }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"hermes-agent timeout ({timeout}s)"}
    except Exception as e:
        return {"ok": False, "error": f"hermes-agent exception: {e}"}


# === SIMPLE MODE (fallback без tools) ===

def parse_sse(body):
    if not body.startswith("data: "):
        return None
    content = ""
    for line in body.split('\n'):
        if line.startswith('data: ') and line != 'data: [DONE]':
            try:
                d = json.loads(line[6:])
                chunk = d.get('choices', [{}])[0].get('delta', {}).get('content', '')
                if not chunk:
                    chunk = d.get('choices', [{}])[0].get('message', {}).get('content', '')
                content += chunk
            except Exception:
                pass
    return content


def ask_brain_simple(prompt, model_name=None, max_tokens=2000, temperature=0.7, system=None):
    """Fallback — голый API без tools. Используется если mode=simple или hermes-agent упал."""
    soul_path = f"{ALINA_HOME}/SOUL.md"
    try:
        soul = open(soul_path).read()[:3000]
    except:
        soul = "Ты — Алина, тёплый личный ассистент Николая. Общайся по-русски, на 'ты', с теплом и юмором."

    effective_system = system or soul

    for name in ([model_name] if model_name else FALLBACK_ORDER):
        if name not in MODELS:
            continue
        cfg = MODELS[name]
        key = ENV.get(cfg["key_env"]) if cfg["key_env"] else None
        if cfg["key_env"] and not key:
            log(f"  {name}: skip (no {cfg['key_env']})")
            continue
        payload = {
            "model": cfg["model"],
            "messages": [],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        if effective_system:
            payload["messages"].append({"role": "system", "content": effective_system})
        payload["messages"].append({"role": "user", "content": prompt})
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        try:
            req = urllib.request.Request(cfg["url"], data=json.dumps(payload).encode(), headers=headers, method="POST")
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=60) as r:
                body_bytes = r.read()
                try:
                    result = json.loads(body_bytes)
                    text = result["choices"][0]["message"]["content"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    text = parse_sse(body_bytes.decode(errors="ignore")) or ""
            if not text:
                log(f"  {name}: empty response")
                continue
            log(f"  {name}: OK ({time.time()-t0:.1f}s, {len(text)} chars)")
            return {"ok": True, "model": name, "text": text, "usage": result.get("usage", {}), "mode": "simple"}
        except Exception as e:
            log(f"  {name}: ERR {e}")
            continue
    return {"ok": False, "error": "All models down"}


# === HTTP HANDLER ===

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def check_auth(self):
        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth[6:]).decode()
            user, pwd = decoded.split(":", 1)
            return user == AUTH_USER and pwd == AUTH_PASS
        except Exception:
            return False

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # === /health/alina — расширенный health с uptime/memory/cron ===
        if self.path == "/health/alina" or self.path == "/health/full":
            import shutil
            mem = shutil.disk_usage("/")
            health = {
                "status": "ok",
                "agent": "ALINA",
                "version": "3.0",
                "uptime": time.time() - START_TIME,
                "memory": {"disk_total_gb": round(mem.total / 1024**3, 1), "disk_free_gb": round(mem.free / 1024**3, 1)},
                "extensions": {
                    "webdav": "ready", "notebooklm": "ready",
                    "ocr": "ready", "yandex_fallback": "ready",
                    "morning_brief": "ready", "inactivity_alert": "ready"
                }
            }
            self.send_json(200, health)
            return

        # === /webdav — читает файл из Obsidian vault ===
        if self.path.startswith("/webdav/"):
            from webdav_client import webdav_get
            sub = self.path[len("/webdav/"):]
            content = webdav_get(sub)
            if content.startswith("["):
                self.send_json(502, {"error": content})
            else:
                self.send_json(200, {"path": sub, "content": content, "length": len(content)})
            return

        if self.path == "/health":
            self.send_json(200, {
                "status": "ok",
                "agent": "ALINA",
                "version": "3.0",
                "port": PORT,
                "auth_user": AUTH_USER,
                "primary_mode": "hermes-agent (with tools)",
                "tools_available": ["browser", "search", "memory", "session_search", "vision", "image_gen", "tts", "todo", "terminal", "skill_manage"],
                "fallback_models": FALLBACK_ORDER,
                "uptime": time.time() - START_TIME,
            })
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if not self.check_auth():
            self.send_json(401, {"error": "unauthorized"})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            data = json.loads(body)
        except Exception:
            self.send_json(400, {"error": "invalid JSON"})
            return

        # === /notebooklm/ask — NotebookLM через Hermes ===
        if self.path == "/notebooklm/ask":
            from notebooklm_client import ask_via_hermes
            q = data.get("query", "")
            if not q:
                self.send_json(400, {"error": "empty query"})
                return
            self.send_json(200, {"ok": True, "answer": ask_via_hermes(q)})
            return

        # === /yandex/search — fallback парсер ===
        if self.path == "/yandex/search":
            from yandex_fallback import search_yandex
            q = data.get("query", "")
            limit = data.get("limit", 10)
            if not q:
                self.send_json(400, {"error": "empty query"})
                return
            self.send_json(200, {"results": search_yandex(q, limit)})
            return

        # === /ocr/receipt — OCR чека ===
        if self.path == "/ocr/receipt":
            from ocr_receipt import ocr_image
            image_path = data.get("image_path", "")
            question = data.get("question", "Извлеки сумму и магазин")
            if not image_path:
                self.send_json(400, {"error": "empty image_path"})
                return
            self.send_json(200, ocr_image(image_path, question))
            return

        # === /morning-brief — генерация сводки (опционально --send) ===
        if self.path == "/morning-brief":
            import subprocess
            send_flag = ["--send"] if data.get("send") else []
            try:
                r = subprocess.run(
                    ["python3.12", "/root/matryoshka/alina/cron/morning_brief.py"] + send_flag,
                    capture_output=True, text=True, timeout=20
                )
                self.send_json(200, {"ok": True, "brief": r.stdout, "sent": bool(send_flag)})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return

        # === /chat и /think — через Hermes Agent (с tools) ===
        if self.path in ("/chat", "/think"):
            user_message = data.get("message") or data.get("prompt", "")
            if not user_message:
                self.send_json(400, {"error": "empty message"})
                return

            # mode: "tools" (default) или "simple" (без tools)
            mode = data.get("mode", "tools")

            if mode == "simple":
                # Fallback на простой API (без tools, прямой HTTP к моделям)
                result = ask_brain_simple(
                    prompt=user_message,
                    model_name=data.get("model"),
                    max_tokens=data.get("max_tokens", 4000 if self.path == "/think" else 2000),
                    temperature=data.get("temperature", 0.3 if self.path == "/think" else 0.7),
                    system=data.get("system") or ("Ты — Алина, напарник Николая. Думай глубоко." if self.path == "/think" else None),
                )
            else:
                # Полный режим: Hermes Agent со ВСЕМИ tools
                sys_prompt = data.get("system") or ("Ты — Алина, напарник Николая. Думай глубоко." if self.path == "/think" else None)
                max_turns = data.get("max_turns", 10)
                timeout = data.get("timeout", 180)
                result = ask_hermes_agent(
                    message=user_message,
                    system=sys_prompt,
                    max_turns=max_turns,
                    timeout=timeout,
                )

            self.send_json(200 if result.get("ok") else 503, result)
            return

        # === /task — задача от HERMES, через Hermes Agent + сохранение ===
        if self.path == "/task":
            task = data.get("task", "")
            if not task:
                self.send_json(400, {"error": "empty task"})
                return
            log(f"TASK от HERMES: {task[:100]}")
            result = ask_hermes_agent(
                message=task,
                max_turns=data.get("max_turns", 15),
                timeout=data.get("timeout", 240),
            )
            if result.get("ok"):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = "".join(c if c.isalnum() else "_" for c in task[:30])
                task_file = ALINA_TASKS / f"DONE_{ts}_{fname}.md"
                with open(task_file, "w") as f:
                    f.write(f"# TASK RESULT ({result.get('model')})\n\n")
                    f.write(f"**Task:** {task}\n\n---\n\n{result.get('text')}\n")
                result["task_file"] = str(task_file)
                log(f"  → {task_file}")
            self.send_json(200 if result.get("ok") else 503, result)
            return

        # === /browser — явный парсинг сайта ===
        if self.path == "/browser":
            url = data.get("url", "")
            if not url:
                self.send_json(400, {"error": "empty url"})
                return
            question = data.get("question", "Что на этой странице?")
            message = f"Зайди на {url} и ответь: {question}"
            result = ask_hermes_agent(message=message, max_turns=8, timeout=120)
            self.send_json(200 if result.get("ok") else 503, result)
            return

        # === /search — явный web search ===
        if self.path == "/search":
            query = data.get("query", "")
            if not query:
                self.send_json(400, {"error": "empty query"})
                return
            message = f"Найди в интернете: {query}. Дай краткий ответ с источниками."
            result = ask_hermes_agent(message=message, max_turns=5, timeout=60)
            self.send_json(200 if result.get("ok") else 503, result)
            return

        # === /skill/{name} — вызвать скилл Алины ===
        if self.path.startswith("/skill/"):
            skill = self.path.replace("/skill/", "")
            args = data.get("args", "")
            message = f"Используй skill '{skill}' с аргументами: {args}"
            result = ask_hermes_agent(message=message, max_turns=10, timeout=120)
            self.send_json(200 if result.get("ok") else 503, result)
            return

        # === /generate-image — генерация картинки ===
        if self.path == "/generate-image":
            prompt = data.get("prompt", "")
            if not prompt:
                self.send_json(400, {"error": "empty prompt"})
                return
            message = f"Сгенерируй изображение: {prompt}"
            result = ask_hermes_agent(message=message, max_turns=8, timeout=180)
            self.send_json(200 if result.get("ok") else 503, result)
            return

        # === /vision — анализ фото ===
        if self.path == "/vision":
            image_url = data.get("image_url", "")
            question = data.get("question", "Что на фото?")
            if not image_url:
                self.send_json(400, {"error": "empty image_url"})
                return
            message = f"Проанализируй фото {image_url}: {question}"
            result = ask_hermes_agent(message=message, max_turns=5, timeout=60)
            self.send_json(200 if result.get("ok") else 503, result)
            return

        self.send_json(404, {"error": "endpoint not found"})


START_TIME = time.time()


def run():
    log(f"Alina server v3.0 starting on :{PORT}")
    log(f"Auth: {AUTH_USER}:{AUTH_PASS[:8]}...")
    log(f"PRIMARY: Hermes Agent (с tools: browser, search, memory, vision, image_gen, tts, todo, terminal)")
    log(f"Fallback: simple API ({FALLBACK_ORDER})")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    log(f"Listening on 0.0.0.0:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
