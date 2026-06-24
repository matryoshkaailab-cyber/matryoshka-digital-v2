#!/usr/bin/env python3
"""
MATRYOSHKA SWARM Router — детерминированный Telegram bot для роя.

Проблема: LLM MiniMax-M3 не следует инструкциям SOUL.md и не вызывает
swarm_send.py через terminal tool. HERMES отвечает Олегу напрямую,
игнорируя swarm протокол.

Решение: отдельный Telegram бот @MatryoshkaSwarmBot (или использует
существующий токен), который сам парсит команды и вызывает swarm_send.py.
LLM (HERMES) остаётся для сложных разговоров, роутинг — детерминированный.

Команды:
  /swarm_alex <cmd>     → ALEX выполнит <cmd>
  /swarm_alf <cmd>      → ALF (стратег) проанализирует <cmd>
  /swarm_alisa <cmd>    → ALISA (отложена, не работает)
  /swarm_status         → статус всех очередей
  /swarm_test           → быстрый тест ALEX
  /swarm_archive [N]    → последние N задач
  /swarm_who            → показать всех агентов
  /swarm_help           → эта справка
"""
import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.parse
import asyncio
from pathlib import Path
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

SWARM_BASE = Path("/root/matryoshka/swarm")
HERMES_CLI = "/usr/local/bin/hermes"
GATEWAY_BOT_TOKEN = "8534368502:AAFPpGFiMAC4KYKzkPxoAbm6sowHVfV_WnM"  # @oleg_industry_bot
OWNER_ID = "1951845052"  # Олег

# Polling state
OFFSET = 0
LAST_POLLER_CHECK = 0
PENDING_TASKS = {}  # task_id -> (chat_id, original_msg)


def log(msg):
    ts = datetime.now().isoformat(timespec="seconds")
    print(f"[{ts}] {msg}", flush=True)


def telegram_api(method, **params):
    """Call Telegram Bot API."""
    url = f"https://api.telegram.org/bot{GATEWAY_BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def send_message(chat_id, text, parse_mode=None, reply_to=None):
    """Send Telegram message."""
    params = {"chat_id": chat_id, "text": text[:4000]}
    if parse_mode:
        params["parse_mode"] = parse_mode
    if reply_to:
        params["reply_to_message_id"] = reply_to
    return telegram_api("sendMessage", **params)


def run_swarm_send(agent: str, command: str, context: str = "") -> dict:
    """Run swarm_send.py as subprocess."""
    # ALEX enforcement (19.06.2026): Obsidian must be fresh before LLM task
    _enforce_r = subprocess.run(["python3", "/usr/local/bin/hermes_obsidian_enforce.py"], capture_output=True, text=True, timeout=30)
    if _enforce_r.returncode == 2:
        return {"ok": False, "error": "Obsidian stale or invalid", "enforce_output": _enforce_r.stdout}

    cmd = [
        "python3", "/root/matryoshka/bin/swarm_send.py", agent, command,
        "--context", context or f"From /swarm_{agent} command"
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return {"ok": False, "error": r.stderr or "swarm_send failed"}
        return json.loads(r.stdout)
    except Exception as e:
        return {"ok": False, "error": str(e)}


def read_archive_task(task_id: str) -> dict | None:
    """Read task result from archive."""
    archive_file = SWARM_BASE / "archive" / f"{task_id}.json"
    if archive_file.exists():
        return json.loads(archive_file.read_text(encoding="utf-8"))
    return None


def wait_for_task_result(task_id: str, timeout: int = 60) -> dict | None:
    """Wait for task to appear in outbox or archive."""
    outbox_file = SWARM_BASE / "outbox" / "alex" / f"{task_id}.json"
    archive_file = SWARM_BASE / "archive" / f"{task_id}.json"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if outbox_file.exists():
            return json.loads(outbox_file.read_text(encoding="utf-8"))
        if archive_file.exists():
            return json.loads(archive_file.read_text(encoding="utf-8"))
        time.sleep(2)
    return None


def cmd_swarm_alex(chat_id, args, reply_to=None):
    """Handle /swarm_alex <command> — ACP direct (sync, no inbox).

    С 18.06.2026: переход с swarm/inbox/alex/ (raw shell, без LLM) на прямой
    ACP канал VPS→ALEX через acp_send.sh. Модель MiniMax-M3 на стороне ALEX
    обрабатывает запрос с tools (bash, edit, read).
    """
    if not args:
        send_message(chat_id, "❌ Использование: `/swarm_alex <command>`\nПример: `/swarm_alex comm_check`", reply_to=reply_to)
        return
    command = " ".join(args)
    send_message(chat_id, f"⏳ Отправляю ALEX через ACP: `{command[:200]}`", reply_to=reply_to)
    # Direct ACP call (sync, через swarm_send_alex.py → acp_send.sh)
    try:
        r = subprocess.run(
            ["python3", "/root/matryoshka/bin/swarm_send_alex.py", command, "--context", "Через /swarm_alex router", "--timeout", "120"],
            capture_output=True, text=True, timeout=150,
        )
        if r.returncode != 0:
            send_message(chat_id, f"❌ ACP ошибка:\n```\n{r.stderr or r.stdout}\n```")
            return
        try:
            result = json.loads(r.stdout)
        except json.JSONDecodeError:
            send_message(chat_id, f"❌ Bad JSON от ACP: `{r.stdout[:500]}`")
            return
        if result.get("ok"):
            output = result.get("output", "")
            elapsed = result.get("elapsed_sec", "?")
            # Extract [ACP] Response: block from acp_send.sh output
            response = output
            if "[ACP] Response:" in output:
                response = output.split("[ACP] Response:")[-1].strip()
            send_message(chat_id, f"✅ ALEX ответил за {elapsed}с:\n```\n{response[:3500]}\n```")
        else:
            err = result.get("error", "?")
            send_message(chat_id, f"❌ ALEX ошибка:\n```\n{err[:3500]}\n```")
    except subprocess.TimeoutExpired:
        send_message(chat_id, "⏰ ALEX timeout 150с")
    except Exception as e:
        send_message(chat_id, f"❌ Router ошибка: {e}")


def cmd_swarm_alf(chat_id, args, reply_to=None):
    """Handle /swarm_alf <prompt>"""
    if not args:
        send_message(chat_id, "❌ Использование: `/swarm_alf <prompt>`\nПример: `/swarm_alf Сделай анализ рынка VPN`")
        return
    prompt = " ".join(args)
    send_message(chat_id, f"⏳ Отправляю ALF: `{prompt[:150]}`", reply_to=reply_to)
    result = run_swarm_send("alf", prompt, "Через /swarm_alf router")
    if not result.get("ok"):
        send_message(chat_id, f"❌ Ошибка отправки: {result.get('error', '?')}")
        return
    task_id = result["task_id"]
    send_message(chat_id, f"🆔 task_id: `{task_id}`\n⏱ Жду ответ от ALF (до 90 сек)...")
    task_result = wait_for_task_result(task_id, timeout=90)
    if not task_result:
        send_message(chat_id, f"⏰ Timeout. ALF не ответил.")
        return
    if task_result.get("ok"):
        out = task_result.get("output", "")
        send_message(chat_id, f"✅ ALF ответил:\n```\n{out[:3500]}\n```")
    else:
        send_message(chat_id, f"❌ ALF ошибка: {task_result.get('error', '?')[:2000]}")


def cmd_swarm_status(chat_id, args, reply_to=None):
    """Handle /swarm_status"""
    lines = ["📊 *Статус роя MATRYOSHKA*\n"]
    for agent in ["alex", "alf", "alisa"]:
        inbox_dir = SWARM_BASE / "inbox" / agent
        outbox_dir = SWARM_BASE / "outbox" / agent
        if inbox_dir.exists():
            inbox_files = list(inbox_dir.glob("*.json"))
            outbox_files = list(outbox_dir.glob("*.json"))
            lines.append(f"  *{agent}*:")
            lines.append(f"    inbox: {len(inbox_files)}")
            lines.append(f"    outbox: {len(outbox_files)}")
        else:
            lines.append(f"  *{agent}*: (offline)")
    archive_count = len(list((SWARM_BASE / "archive").glob("*.json"))) if (SWARM_BASE / "archive").exists() else 0
    lines.append(f"\n  Archive: {archive_count} total")
    # Check services
    r = subprocess.run(["systemctl", "is-active", "swarm-poller"], capture_output=True, text=True, timeout=5)
    lines.append(f"  swarm-poller: {r.stdout.strip()}")
    send_message(chat_id, "\n".join(lines), parse_mode="Markdown", reply_to=reply_to)


def cmd_swarm_test(chat_id, args, reply_to=None):
    """Handle /swarm_test — быстрый тест ALEX"""
    send_message(chat_id, "🧪 Тест роя: отправляю ALEX простую задачу...", reply_to=reply_to)
    result = run_swarm_send("alex", "echo PONG_FROM_ROUTER_$(date +%H%M%S)", "Test from /swarm_test")
    if not result.get("ok"):
        send_message(chat_id, f"❌ {result.get('error', '?')}")
        return
    task_id = result["task_id"]
    send_message(chat_id, f"🆔 {task_id} — жду ответ...")
    task_result = wait_for_task_result(task_id, timeout=30)
    if task_result and task_result.get("ok"):
        out = task_result.get("output", "").strip()
        send_message(chat_id, f"✅ ALEX живой!\nОтвет: `{out[:200]}`")
    else:
        send_message(chat_id, f"❌ ALEX не ответил или ошибка. Проверь worker на ПК.")


def cmd_swarm_archive(chat_id, args, reply_to=None):
    """Handle /swarm_archive [N=5]"""
    n = 5
    if args:
        try:
            n = int(args[0])
        except ValueError:
            pass
    archive_dir = SWARM_BASE / "archive"
    if not archive_dir.exists():
        send_message(chat_id, "❌ Archive не существует", reply_to=reply_to)
        return
    files = sorted(archive_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:n]
    if not files:
        send_message(chat_id, "📭 Archive пуст", reply_to=reply_to)
        return
    lines = [f"📚 *Последние {len(files)} задач:*\n"]
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            tid = data.get("task_id", "?")
            ok = "✅" if data.get("ok") else "❌"
            finished = data.get("finished_at", "?")[:19]
            out_preview = (data.get("output") or "").replace("\n", " ")[:60]
            lines.append(f"{ok} `{tid}` @ {finished}")
            if out_preview:
                lines.append(f"   `{out_preview}`")
        except Exception as e:
            lines.append(f"⚠️ {f.name}: {e}")
    send_message(chat_id, "\n".join(lines), parse_mode="Markdown", reply_to=reply_to)


def cmd_swarm_who(chat_id, args, reply_to=None):
    """Handle /swarm_who — список агентов"""
    msg = """🐝 *Рой MATRYOSHKA — Состав*

⚪ *HERMES* (дирижёр) — @oleg_industry_bot
   МиниMax-M3, VPS, gateway PID 2128970
   ⚠️ Не вызывает swarm_send.py — используйте /swarm_* напрямую

⚪ *ALF* (стратег) — @IlonAnalyticBot
   МиниMax-M3, VPS, profile=alf, gateway PID 2372137
   Доступен через /swarm_alf

🔵 *ALEX* (техник) — Windows ПК
   Scheduled Task ALEX_HERMES_Worker
   Доступен через /swarm_alex

🔴 *ALISA* (контент) — отложена

👤 *ALINA* (клиентский) — @NikolaAlinaBot, для Николая
   НЕ часть роя Олега

🔧 *Инфраструктура роя:*
   • /root/matryoshka/swarm/{inbox,outbox,archive}/
   • swarm-poller.service (PID 2361567)
   • swarm_watchdog (cron */5)
   • ALEX worker на ПК (Scheduled Task)
"""
    send_message(chat_id, msg, parse_mode="Markdown", reply_to=reply_to)


def cmd_swarm_help(chat_id, args, reply_to=None):
    """Handle /swarm_help"""
    msg = """🐝 *SWARM Router — Команды*

`/swarm_alex <cmd>` — ALEX выполнит (технические задачи)
   Пример: `/swarm_alex ssh root@10.8.1.1 'df -h /'`

`/swarm_alf <prompt>` — ALF проанализирует (стратегия)
   Пример: `/swarm_alf Сделай анализ рынка VPN`

`/swarm_status` — статус всех очередей + services

`/swarm_test` — быстрый тест ALEX

`/swarm_archive [N=5]` — последние N задач с результатами

`/swarm_who` — список всех агентов

`/swarm_help` — эта справка

💡 *Этот роутер обходит LLM* — он напрямую вызывает swarm_send.py
без участия HERMES/ALF. Поэтому работает железно.
"""
    send_message(chat_id, msg, parse_mode="Markdown", reply_to=reply_to)


def handle_message(msg):
    """Process one Telegram message."""
    global OFFSET
    text = msg.get("text", "").strip()
    chat_id = msg["chat"]["id"]
    user_id = str(msg.get("from", {}).get("id", ""))
    if user_id != OWNER_ID:
        log(f"ignore: user {user_id} (not owner)")
        return
    if not text.startswith("/"):
        # Not a command — ignore (let HERMES handle)
        return
    log(f"cmd from {user_id}: {text[:80]}")
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower().split("@")[0]  # remove @botname
    args = parts[1].split() if len(parts) > 1 else []
    reply_to = msg.get("message_id")
    if cmd == "/swarm_alex":
        cmd_swarm_alex(chat_id, args, reply_to)
    elif cmd == "/swarm_alf":
        cmd_swarm_alf(chat_id, args, reply_to)
    elif cmd == "/swarm_status":
        cmd_swarm_status(chat_id, args, reply_to)
    elif cmd == "/swarm_test":
        cmd_swarm_test(chat_id, args, reply_to)
    elif cmd == "/swarm_archive":
        cmd_swarm_archive(chat_id, args, reply_to)
    elif cmd == "/swarm_who":
        cmd_swarm_who(chat_id, args, reply_to)
    elif cmd == "/swarm_help":
        cmd_swarm_help(chat_id, args, reply_to)
    elif cmd in ("/start", "/help"):
        cmd_swarm_help(chat_id, args, reply_to)
    # Other commands — let HERMES handle them via normal flow


def main():
    global OFFSET
    log("MATRYOSHKA Swarm Router started")
    log(f"Owner: {OWNER_ID}, bot: @oleg_industry_bot (HERMES gateway)")
    log(f"Watching for /swarm_* commands")
    while True:
        try:
            url = f"https://api.telegram.org/bot{GATEWAY_BOT_TOKEN}/getUpdates?offset={OFFSET}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            for upd in data.get("result", []):
                OFFSET = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg:
                    continue
                # Only handle our commands, let HERMES handle the rest
                text = msg.get("text", "").strip()
                if text.startswith("/swarm_") or text in ("/start", "/help"):
                    handle_message(msg)
        except Exception as e:
            log(f"loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
