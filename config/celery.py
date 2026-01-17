import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Change this: Remove the namespace='CELERY'
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()