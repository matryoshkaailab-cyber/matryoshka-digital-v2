# VPN — Конфиги и ключи

## Серверный конфиг AmneziaWG
```
Файл: /etc/amnezia/amneziawg/awg0.conf
```

### BLEICH параметры (для клиента!)
```ini
Jc   = 4
Jmin = 84
Jmax = 243
S1   = 35
S2   = 99
S3   = 24
S4   = 8
H1   = 100000-800000
H2   = 1000000-8000000
H3   = 10000000-80000000
H4   = 100000000-800000000
I1   = <r 256>
MTU  = 1280
DNS  = 1.1.1.1
```

## Ключи сервера
```
PrivateKey:  0Ad1Ia2F1n+QAFQMBxosV5kh5kjcftG1IsqEKm9SEXk=
PublicKey:   r1H9WNYCogOjf/x+3eoo2OGhN6Qnt8LlhQc721OlsHM=
```

## VLESS ключи
```
Private Key: iEQzCq-eDrJBDXsj7XHT0TihC0z7ezBAEb0567UqkUw
Public Key:  3lQAUlk9WBzJgr6Spb9eT7C5j47tpuLFY0SR_dmNFik
Short ID:    4818db014702038b
```

## Шаблон клиентского .conf
```ini
[Interface]
PrivateKey = <CLIENT_PRIVATE_KEY>
Address    = 10.9.9.X/32
DNS        = 1.1.1.1
MTU        = 1280
Jc         = 4
Jmin       = 84
Jmax       = 243
S1         = 35
S2         = 99
S3         = 24
S4         = 8
H1         = 100000-800000
H2         = 1000000-8000000
H3         = 10000000-80000000
H4         = 100000000-800000000
I1         = <r 256>

[Peer]
PublicKey           = r1H9WNYCogOjf/x+3eoo2OGhN6Qnt8LlhQc721OlsHM=
Endpoint            = 85.137.166.209:41234
AllowedIPs          = 0.0.0.0/0, ::/0
PersistentKeepalive = 25   # WiFi: 25, CGNAT: 10
```

## Бот
```
Файл на сервере: /root/datalink_pro_bot_v12.py
Токен: 8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I
Бот: @datalink_pro_bot
```
