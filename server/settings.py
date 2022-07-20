
# redis config
REDIS_HOST = ''
REDIS_PORT = 6379
REDIS_DB = 0


# broker config
CELERY_BROKER_URL = ''
CELERY_BACKEND_URL = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)

static_file_dir = 'static'

HOST_IP = ''
DOMAIN = ''