from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from .models import VideoModel


class ApiView(View):
    def get(self, request):
        page_no = request.GET.get("page", 1)
        title = request.GET.get("title", None)
        description = request.GET.get("description", None)

        videos = VideoModel.objects.all().order_by("-date")
        if title:
            videos = videos.filter(title__icontains == title)
        if description:
            videos = videos.filter(description__icontains == description)

        pages = Paginator(videos, 50)

        try:
            page = pages.page(page_no)
        except PageNotAnInteger:
            return JsonResponse({"msg": "Page not an integer"}, status=404)
        except EmptyPage:
            page = pages.page(pages.num_pages)
            page_no = pages.num_pages

        return JsonResponse(
            {"page_no": page_no, "total_pages": pages.num_pages, "videos": list(page)}
        )
