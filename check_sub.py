#!/usr/bin/env python3
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for host in ['vpn.xn----7sbaowmfrljlq.xn--p1ai', 'dl.matryoshka-digital.ru']:
    try:
        req = urllib.request.Request(
            f'https://dl.matryoshka-digital.ru:8443/subscribe/1951845052',
            headers={'Host': host}
        )
        r = urllib.request.urlopen(req, context=ctx, timeout=5)
        data = r.read(200)
        print(f'{host}: OK -> {data[:100]}')
    except Exception as e:
        print(f'{host}: ERR -> {e}')
