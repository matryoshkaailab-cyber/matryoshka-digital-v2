# DATALINK VPN — Health Check Alert
# $(date)

## 🔴 CRITICAL: Reality VPN DISABLED — x-ui overwrote config!

### Current state (WRONG):
- inbound-443 on :443 — xHTTP + TLS (NOT Reality!)
- No Reality inbounds
- Clients cannot connect via Reality protocol

### Evidence:
$(python3 /tmp/verify_reality.py)

### Required action:
Restore Reality config using keys from /root/matryoshka/reality-keys-20260429.txt

### Config to restore:
- Port: 443 (Reality Vision)
- SNI: www.bing.com (Microsoft TLS)
- PrivateKey: UOW9SYxgPjGBP1HkkUMFFAxs4we-8Q4MEFcbnNAZMlc
- PublicKey: er7qUhwuJYHI1xx-I-11DtDnDbcmzy12bK7JVFyTdw0
- ShortID: 42ba5a090b2bdeaa
- UUID: 4ea33e69-8a88-4811-b1f7-e433b46b8f5a
- Flow: xtls-rprx-vision
