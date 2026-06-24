"""
webdav_client.py — Алина читает Obsidian vault через WebDAV.

WebDAV сервер: https://85.137.166.209:8181 (nginx)
Auth: hermes:hermes2026 (из alf/librarian.env)
Mount point: /root/obsidian-vault/
"""
import os
import urllib.request
import urllib.parse
import urllib.error
import base64
import ssl
from pathlib import Path
from typing import Optional


def _get_auth():
    """Читает WEBDAV_USER/PASSWORD из env или .env."""
    user = os.environ.get("WEBDAV_USER", "hermes")
    pwd = os.environ.get("WEBDAV_PASSWORD", "")
    if not pwd:
        for env_file in [
            Path("/root/matryoshka/alf/librarian.env"),
            Path("/root/.hermes/profiles/alina/.env"),
            Path("/root/.hermes/profiles/hermes-cli/.env"),
        ]:
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith("WEBDAV_PASSWORD="):
                        pwd = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if pwd:
                            break
                if pwd:
                    break
    return user, pwd


WEBDAV_BASE = os.environ.get("WEBDAV_URL", "https://85.137.166.209:8181")
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def webdav_get(path: str, timeout: int = 10) -> str:
    if path.startswith("/"):
        path = path[1:]
    url = f"{WEBDAV_BASE.rstrip('/')}/{urllib.parse.quote(path)}"
    user, pwd = _get_auth()
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Basic {base64.b64encode(f'{user}:{pwd}'.encode()).decode()}")
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}: {e.reason}]"
    except Exception as e:
        return f"[ERR: {e}]"


def read_obsidian(path: str) -> str:
    return webdav_get(path)


def read_agents_md() -> str:
    return webdav_get("agents/AGENTS_REGISTRY.md")


def read_priority_plan() -> str:
    return webdav_get("PRIORITY_PLAN.md")


def read_alina_full() -> str:
    return webdav_get("ALF_FULL.md")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(webdav_get(path)[:500])
    else:
        print("=== Тест WebDAV ===")
        for path in ["00_INDEX.md", "PRIORITY_PLAN.md", "agents/alf/README.md", "AGENTS/HERMES.md"]:
            print(f"\n--- {path} ---")
            content = webdav_get(path)
            if content.startswith("[") and "]" in content[:10]:
                print(f"  ERROR: {content[:200]}")
            else:
                print(f"  OK ({len(content)} chars): {content[:150]}...")
