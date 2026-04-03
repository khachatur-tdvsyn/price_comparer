# project_name/celery.py
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_comparer.settings')

app = Celery('price_comparer')

# Load config from Django settings, using 'CELERY' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all registered apps
app.autodiscover_tasks()