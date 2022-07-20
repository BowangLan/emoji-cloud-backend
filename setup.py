import os
import sys
import re


HOST_IP = sys.argv[1]


content = '''
server {
  listen 80;

  server_name {HOST_IP};

  location /api {
    rewrite ^/api/(.*)$ /$1 break;
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }

  location / {
    proxy_pass http://localhost:3000;
  }
}
'''.replace('{HOST_IP}', HOST_IP)


with open('/etc/nginx/conf.d/default.conf', 'w') as f:
    f.write(content)

with open('client/next.config.js', 'r') as f:
    content = f.read()
new_content = re.sub(r"HOST_IP: '.*?'", "HOST_IP: '{}'".format(HOST_IP), content)
new_content = re.sub("DEV: \"TRUE\"", "DEV: \"FALSE\"", content)
with open('client/next.config.js', 'w') as f:
    f.write(new_content)
    

