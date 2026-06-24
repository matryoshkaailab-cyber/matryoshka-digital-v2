# Инфраструктура MATRYOSHKA DIGITAL

## VPS
- IP: 85.137.166.209
- Host: SmartApe (Чехия)
- OS: Ubuntu 24.04
- SSH: root/Jktu22051987

## Сервисы и порты
- 22 — SSH
- 443 — Xray VLESS+Reality VPN (x-ui)
- 2053 — VLESS alt
- 4096 — opencode ACP
- 5678 — n8n
- 8181 — nginx WebDAV (Obsidian sync)
- 8446 — alex_bridge HTTP (ПК)
- 8448 — ALISA API
- 8451 — ALF HTTP API
- 8453 — vps_tunnel_bridge
- 8765 — Qwen2api local

## Домены
- xn----7sbaowmfrljlq.xn--p1ai (VPN)
- vpn.xn----7sbaowmfrljlq.xn--p1ai (webhook)

## Агенты
- HERMES — порт активен, systemd hermes-cli-gateway
- ALF — :8451, systemd hermes-alf
- ALINA — @NikolaAlinaBot, systemd hermes-alina
- ALEX — opencode 1.17.3 на ПК через AWG 10.8.1.4
