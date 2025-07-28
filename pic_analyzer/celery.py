import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pic_analyzer.settings')

app = Celery('pic_analyzer', broker='sqs://')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()