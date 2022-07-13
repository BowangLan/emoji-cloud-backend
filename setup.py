import os
import sys

with open('default.conf', 'r') as f:
    content = f.read()

content = content.format(HOST_IP=os.environ.get('HOST_IP'),
               DOMAIN=os.environ.get('DOMAIN'))

with open('/etc/nginx/conf.d/default.conf', 'w') as f:
    f.write(content)
