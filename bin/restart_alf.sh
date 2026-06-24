#!/bin/bash
# Restart ALF gateway после patch config (Nemotron switch)
# Запускается через at/cron чтобы обойти sandbox block

set -e
LOG="/root/matryoshka/logs/restart_alf_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /root/matryoshka/logs

{
  echo "=== ALF restart initiated $(date -u) ==="
  echo "--- Pre-restart status ---"
  systemctl is-active hermes-gateway-alf.service
  ps -eo pid,etime,cmd | grep -E 'hermes_cli.main --profile alf' | grep -v grep
  echo "--- Restarting ---"
  systemctl restart hermes-gateway-alf.service
  echo "--- Waiting 15s ---"
  sleep 15
  echo "--- Post-restart status ---"
  systemctl is-active hermes-gateway-alf.service
  ps -eo pid,etime,cmd | grep -E 'hermes_cli.main --profile alf' | grep -v grep
  echo "--- Healthcheck ---"
  curl -sS --max-time 5 http://127.0.0.1:8452/health
  echo ""
  echo "--- Recent logs ---"
  journalctl -u hermes-gateway-alf -n 15 -o cat --no-pager
  echo "=== ALF restart done $(date -u) ==="
} > "$LOG" 2>&1 &
