import os

# redis config
REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
REDIS_DB = os.environ.get('REDIS_DB') or 0

CANCELLED_TASK_REDIS_KEY = 'cancelled_tasks'
RUNNING_TASK_REDIS_KEY = 'running_tasks'
RESULT_KEY = 'task_results'
FAILED_TASK_REDIS_KEY = 'failed_tasks'


# broker config
CELERY_BACKEND_URL = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)
CELERY_BROKER_URL = CELERY_BACKEND_URL

static_file_dir = 'static'

HOST_IP = ''
DOMAIN = ''