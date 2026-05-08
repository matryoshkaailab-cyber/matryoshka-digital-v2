#!/usr/bin/env python3
import http.client
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = http.client.HTTPSConnection('dl.matryoshka-digital.ru', 8443, context=ctx)
conn.request('GET', '/subscribe/7453044462', headers={'Host': 'vpn.xn----7sbaowmfrljlq.xn--p1ai'})
r = conn.getresponse()
print(r.status, r.reason)
data = r.read(500)
print(data[:200])
