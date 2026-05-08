#!/bin/bash
# Patch nginx.conf to add subscribe/webhook proxy
CONF="/etc/nginx/nginx.conf"
BACKUP="$CONF.bak.$(date +%s)"

cp "$CONF" "$BACKUP"

# Find the line with "index index.html;" in the http server block and add locations after it
python3 << 'PYEOF'
import re

with open('/etc/nginx/nginx.conf', 'r') as f:
    content = f.read()

# Find the http {} block and add location blocks after index.html
location_block = '''
        location /subscribe/ {
            proxy_pass http://127.0.0.1:5001/subscribe/;
            proxy_set_header Host $host;
        }
        location /webhook/ {
            proxy_pass http://127.0.0.1:5001/webhook/;
            proxy_set_header Host $host;
        }
        location /site/ {
            proxy_pass http://127.0.0.1:5001/site/;
            proxy_set_header Host $host;
        }'''

# Insert after "index index.html;" within the http server block
pattern = r'(        index index\.html;)(\n)'
replacement = r'\1\2' + location_block + '\n'

new_content = re.sub(pattern, replacement, content)

with open('/etc/nginx/nginx.conf', 'w') as f:
    f.write(new_content)

print("Patched nginx.conf")
PYEOF

nginx -t 2>&1
