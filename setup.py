import os
import sys


HOST_IP = sys.argv[1]


nginx_default_conf_content = '''
server {
  listen 80;

  server_name 18.236.231.247;
  # server_name _;

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
