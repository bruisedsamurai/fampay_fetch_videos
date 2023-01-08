from django.contrib import admin

from .models import VideoModel


class VideoAdmin(admin.ModelAdmin):
    fields = ["date", "title", "description", "video_id", "thumbnail"]
    list_filter = [
        "date",
    ]
    sortable_by = ["date", "title", "video_id"]


admin.site.register(VideoModel, VideoAdmin)
