#!/usr/bin/env python3.12
"""
ALINA Metrics Collector — Prometheus-like endpoint.
Собирает метрики: uptime, requests, errors, latency.
Отдаёт в формате Prometheus text на /metrics.
"""
import json
import time
import os
import re
import urllib.request
import urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime

ALINA_HOME = Path("/root/.hermes/profiles/alina")
ALINA_TASKS = Path("/root/matryoshka/alina_tasks")
LOGS = {
    "gateway": "/var/log/alina-gateway.log",
    "server": "/var/log/alina_server.log",
    "avito": "/var/log/alina_avito.log",
    "finance": "/var/log/alina_finance.log",
    "weekly": "/var/log/alina_weekly.log",
    "kb": "/var/log/alina_kb.log",
    "backup": "/var/log/alina_backup.log",
    "bridge": "/var/log/alina_bridge.log",
    "watchdog": "/var/log/alina_watchdog.log",
}

METRICS = {
    "alina_uptime_seconds": 0,
    "alina_requests_total": 0,
    "alina_errors_total": 0,
    "alina_latency_avg_ms": 0,
    "alina_tokens_total": 0,
    "alina_skills_count": 0,
    "alina_cron_count": 0,
    "alina_tasks_count": 0,
    "alina_status": 0,  # 1=ok, 0=down
    "alina_cron_last_success": {},  # cron name → timestamp
    "alina_logs_size_bytes": {},  # log name → bytes
}

START_TIME = time.time()


def parse_logs():
    """Парсит логи для сбора метрик."""
    total_requests = 0
    total_errors = 0
    total_latency = 0
    total_tokens = 0

    # server log: HTTP запросы (custom format: "[time] METHOD /path status latency_ms")
    server_log = Path(LOGS["server"])
    if server_log.exists():
        try:
            for line in server_log.read_text().split("\n")[-1000:]:  # последние 1000 строк
                m = re.search(r"(\d+)ms", line)
                if m:
                    total_latency += int(m.group(1))
                    total_requests += 1
                if "error" in line.lower() or "500" in line or "503" in line:
                    total_errors += 1
        except Exception:
            pass

    # gateway log: подсчёт сообщений от Telegram
    gateway_log = Path(LOGS["gateway"])
    if gateway_log.exists():
        try:
            content = gateway_log.read_text()
            # Считаем POST /sendMessage (отправки)
            sends = content.count("/sendMessage")
            METRICS["alina_requests_total"] = sends
        except Exception:
            pass

    # Tasks count
    if ALINA_TASKS.exists():
        METRICS["alina_tasks_count"] = len(list(ALINA_TASKS.glob("*.md")))

    # Skills
    skills_dir = ALINA_HOME / "skills"
    if skills_dir.exists():
        METRICS["alina_skills_count"] = len([s for s in skills_dir.iterdir() if s.name != ".bundled_manifest"])

    # Cron
    cron_dir = Path("/etc/cron.d")
    METRICS["alina_cron_count"] = len([f for f in cron_dir.iterdir() if f.name.startswith("alina-")])

    # Logs size
    for name, path in LOGS.items():
        p = Path(path)
        if p.exists():
            METRICS["alina_logs_size_bytes"][name] = p.stat().st_size

    METRICS["alina_uptime_seconds"] = int(time.time() - START_TIME)
    METRICS["alina_latency_avg_ms"] = total_latency // total_requests if total_requests else 0
    METRICS["alina_errors_total"] = total_errors


def collect_prometheus():
    """Возвращает текст в формате Prometheus."""
    parse_logs()
    lines = []
    lines.append("# HELP alina_uptime_seconds Seconds since alina-metrics start")
    lines.append("# TYPE alina_uptime_seconds gauge")
    lines.append(f"alina_uptime_seconds {METRICS['alina_uptime_seconds']}")

    lines.append("# HELP alina_status 1 if alina is operational")
    lines.append("# TYPE alina_status gauge")
    lines.append(f"alina_status {METRICS['alina_status']}")

    lines.append("# HELP alina_requests_total Total requests processed")
    lines.append("# TYPE alina_requests_total counter")
    lines.append(f"alina_requests_total {METRICS['alina_requests_total']}")

    lines.append("# HELP alina_errors_total Total errors")
    lines.append("# TYPE alina_errors_total counter")
    lines.append(f"alina_errors_total {METRICS['alina_errors_total']}")

    lines.append("# HELP alina_latency_avg_ms Average latency in milliseconds")
    lines.append("# TYPE alina_latency_avg_ms gauge")
    lines.append(f"alina_latency_avg_ms {METRICS['alina_latency_avg_ms']}")

    lines.append("# HELP alina_skills_count Number of active skills")
    lines.append("# TYPE alina_skills_count gauge")
    lines.append(f"alina_skills_count {METRICS['alina_skills_count']}")

    lines.append("# HELP alina_cron_count Number of cron jobs")
    lines.append("# TYPE alina_cron_count gauge")
    lines.append(f"alina_cron_count {METRICS['alina_cron_count']}")

    lines.append("# HELP alina_tasks_count Number of files in alina_tasks/")
    lines.append("# TYPE alina_tasks_count gauge")
    lines.append(f"alina_tasks_count {METRICS['alina_tasks_count']}")

    lines.append("# HELP alina_logs_size_bytes Log file sizes")
    lines.append("# TYPE alina_logs_size_bytes gauge")
    for name, size in METRICS["alina_logs_size_bytes"].items():
        lines.append(f'alina_logs_size_bytes{{log="{name}"}} {size}')

    return "\n".join(lines) + "\n"


def check_alina_health():
    """Проверяет что gateway и server отвечают."""
    try:
        with urllib.request.urlopen("http://localhost:8470/health", timeout=3) as r:
            data = json.loads(r.read())
            METRICS["alina_status"] = 1 if data.get("status") == "ok" else 0
    except Exception:
        METRICS["alina_status"] = 0


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # тишина

    def do_GET(self):
        if self.path == "/metrics":
            check_alina_health()
            body = collect_prometheus().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/":
            body = ("ALINA Metrics — see /metrics\n").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    PORT = int(os.environ.get("ALINA_METRICS_PORT", 8471))
    print(f"📊 ALINA metrics on :{PORT}/metrics")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
