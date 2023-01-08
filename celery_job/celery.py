import os
import sys
from celery import Celery


import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fetch_videos.settings")


celery_app = Celery("fetch_videos")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
