from pathlib import Path

from django.http import JsonResponse
from django.urls import path

from rest_framework.permissions import AllowAny


def health(request):
    return JsonResponse({"status": "ok", "service": "ORBITE API"})


urlpatterns = [
    path("", health, name="health"),
]