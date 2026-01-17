# import os
# from celery import Celery
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
#
# app = Celery('config')
#
# # Change this: Remove the namespace='CELERY'
# app.config_from_object('django.conf:settings')
#
# app.autodiscover_tasks()

import os
from celery import Celery

# 1. Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Get the Redis URL directly from the environment
# This ensures the worker has the URL before it even looks at Django settings.
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# 3. Pass the broker and backend DIRECTLY into the constructor
app = Celery('config', broker=redis_url, backend=redis_url)

# 4. Load remaining settings (like task limits) from Django settings
# We REMOVE the namespace='CELERY' to allow more flexible naming
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()