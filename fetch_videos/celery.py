import os
from celery import Celery

from .tasks import task_add_videos

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fetch_videos.settings")

celery_app = Celery("fetch_videos")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        10.0,
        task_add_videos.s(os.environ.get("YOUTUBE_KEY")),
        name="fetch video detaials every 10 seconds",
    )


@celery_app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
