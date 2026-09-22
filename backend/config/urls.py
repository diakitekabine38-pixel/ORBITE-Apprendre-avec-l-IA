from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
from django.views.static import serve as media_serve

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def spa(request, path=""):
    """Single-page fallback — serves the built React app for any non-API route."""
    index = settings.FRONTEND_DIST / "index.html"
    body = index.read_bytes() if index.exists() else b"<h1>Frontend non build\u00e9.</h1>"
    return HttpResponse(body, content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1 — main REST contract
    path("api/v1/", include("config.api_urls")),
    # Health check
    path("api/health/", include("apps.common.urls")),
    # Media (uploaded files) — local production serving
    re_path(r"^media/(?P<path>.*)$", media_serve, {"document_root": settings.MEDIA_ROOT}),
]

# SPA fallback: everything that is not API/admin/media/static gets the React app.
urlpatterns.append(
    re_path(r"^(?!api/|admin/|media/|static/).*", spa, name="spa"),
)