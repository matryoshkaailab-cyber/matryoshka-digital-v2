#!/bin/bash
# Восстановление VLESS Reality Vision на порт 2053

# 1. Kill xray
pkill -f "xray-linux-amd64" 2>/dev/null
sleep 1

# 2. Создать новый конфиг с Reality
cat > /usr/local/x-ui/bin/config.json << 'EOF'
{
  "log": {
    "access": "none",
    "error": "",
    "loglevel": "warning"
  },
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {"type": "field", "inboundTag": ["api"], "outboundTag": "api"},
      {"type": "field", "outboundTag": "blocked", "ip": ["geoip:private"]},
      {"type": "field", "outboundTag": "blocked", "protocol": ["bittorrent"]}
    ]
  },
  "inbounds": [
    {
      "listen": "0.0.0.0",
      "port": 2053,
      "protocol": "vless",
      "settings": {
        "clients": [{"id": "4ea33e69-8a88-4811-b1f7-e433b46b8f5a", "email": "datalink@vpn", "flow": "xtls-rprx-vision"}],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.microsoft.com:443",
          "serverNames": ["www.microsoft.com"],
          "privateKey": "0RwL82gpgkgpGCqrX7rMYpC1A6xPbPG6gJK9hqQ2QX0",
          "shortIds": [""]
        },
        "tcpSettings": {"header": {"type": "none"}}
      },
      "tag": "inbound-2053",
      "sniffing": {"enabled": true, "destOverride": ["http", "tls"]}
    },
    {
      "listen": "127.0.0.1",
      "port": 62789,
      "protocol": "tunnel",
      "settings": {"address": "127.0.0.1"},
      "tag": "api"
    }
  ],
  "outbounds": [
    {"tag": "direct", "protocol": "freedom", "settings": {}},
    {"tag": "blocked", "protocol": "blackhole", "settings": {}}
  ],
  "api": {"tag": "api", "services": ["HandlerService", "LoggerService", "StatsService"]},
  "stats": {},
  "policy": {
    "levels": {"0": {"statsUserDownlink": true, "statsUserUplink": true}},
    "system": {"statsInboundDownlink": true, "statsInboundUplink": true, "statsOutboundDownlink": false, "statsOutboundUplink": false}
  }
}
EOF

# 3. Запустить xray
cd /usr/local/x-ui && nohup ./bin/xray-linux-amd64 run -c ./bin/config.json > /var/log/xray.log 2>&1 &
sleep 2

# 4. Проверить
if ss -tlnp | grep -q 2053; then
  echo "✅ VPN ЗАПУЩЕН на порту 2053"
  echo "UUID: 4ea33e69-8a88-4811-b1f7-e433b46b8f5a"
  echo "SNI: www.microsoft.com"
  echo "Flow: xtls-rprx-vision"
else
  echo "❌ ОШИБКА ЗАПУСКА"
  cat /var/log/xray.log
fi