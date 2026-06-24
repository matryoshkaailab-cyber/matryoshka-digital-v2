# HERMES Memory — MATRYOSHKA DIGITAL
## Updated: 2026-05-27 21:45

## System
- VPS: 85.137.166.209 (Ubuntu 24.04, 8GB RAM, 50GB disk)
- Projects: /root/matryoshka/
- Hermes config: /root/.hermes/config.yaml

## Tool quirks (important)
- vision_analyze: BROKEN (401 OpenRouter key missing). MiniMax-M2.7 native inline vision WORKS — "Image routing: native" in logs. Use inline, NOT vision_analyze tool.
- terminal: use read_file/patch/write_file, NOT cat/sed/echo
- browser: file:// protocol fails (ERR_ACCESS_DENIED)
- ALEX: ws via port 8446, HTTP fallback 9000→alex_router:4000

## Projects
- MATRYOSHKA: /root/matryoshka/ (bots, agents, cases, n8n)
- DATALINK PRO VPN: VLESS+Reality port 443, UUID 4ea33e69-8a88-4811-b1f7-e433b46b8f5a
- ALISA 2.0: bot.py PID 2105546, api.py PID 2027745 (port 8448)

## Users
- Oleg (@oleglab22): жёсткий, матерный, НЕ терпит вранья. "Сделай X" = делай сразу. Голосовые не читает.
- Natalia (ID:461605744): гончарная школа «Зарни Ань», Эклер бот

## Open issues
1. ALEX ws_connection broken (since 25.05.2026)
2. VPS disk 75% — needs cleanup
3. vision_analyze 401 — needs OpenRouter key or MiniMax Vision

## Active services
- Docker: n8n, amnezia-awg2, mtproto-proxy, open-design
- Kanban: 0 pending tasks


---
_Memory bridge export. Source: `/root/.hermes/MEMORY.md`_
_Exported: 2026-06-04 07:05:34 UTC_
