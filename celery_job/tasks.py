import os
import datetime
from typing import List, Dict, Optional
import logging

from django.db.utils import IntegrityError

from celery import shared_task
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from fetch_videos.models import VideoModel

from .celery import celery_app


logger = logging.Logger(__file__)


def parse_videos(items):
    videos: List[VideoModel] = []
    for item in items:
        date = datetime.datetime.strptime(
            item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        )
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        video_id = item["id"]["videoId"]
        thumbnail = item["snippet"]["thumbnails"]["high"]
        video = VideoModel(
            date=date,
            title=title,
            description=description,
            video_id=video_id,
            thumbnail=thumbnail,
        )
        errors = video.check()
        if errors:
            raise Exception(errors)
        videos.append(video)
    return videos


def fetch_videos(keys: List[str]) -> List[VideoModel]:
    api_service_name = "youtube"
    api_version = "v3"
    keys_iter = iter(keys)
    DEVELOPER_KEY = next(keys_iter)
    key_no = 0

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    date = datetime.datetime.now() - datetime.timedelta(days=365)

    items = []
    page_token = None
    while True:
        try:
            # https://developers.google.com/youtube/v3/docs/search/list
            request = youtube.search().list(
                part="snippet",
                type="video",
                order="date",
                publishedAfter=date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                q="music",
                maxResults=50,
                **({"pageToken": page_token} if page_token else {})
            )
            response = request.execute()
            if len(response["items"]) == 0 or not response.get("nextPageToken"):
                break
            items.extend(response["items"])

        except HttpError as e:
            logger.error(e)
            if e.resp.status == 403:
                try:
                    key = next(keys_iter)
                except StopIteration:
                    break
                DEVELOPER_KEY = key
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=DEVELOPER_KEY
                )

    return parse_videos(items)


@shared_task
def task_add_videos(
    keys,
):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    videos = fetch_videos(keys)  # type: ignore
    print(videos)

    try:
        result = VideoModel.objects.bulk_create(videos)
    except IntegrityError:
        result = VideoModel.objects.bulk_create(videos, batch_size=10)
    return result


from fetch_videos.settings import YOUTUBE_KEYS

celery_app.add_periodic_task(10, task_add_videos.s(YOUTUBE_KEYS))
