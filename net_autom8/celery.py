from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, shared_task


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'net_autom8.settings')
app = Celery('net_autom8')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
