"""Django settings for the ORBITE platform.

Configuration is read from environment variables so the same codebase can run
in development, testing and production. Never hardcode secrets.
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env if present (existing shell variables always take priority).
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Secrets — ALWAYS injected through the environment, never committed.
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "ORBITE_SECRET_KEY",
    "django-insecure-dev-only-change-me-in-production",
)
DEBUG = os.environ.get("ORBITE_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ORBITE_ALLOWED_HOSTS", "*").split(",")

# ---------------------------------------------------------------------------
# Applications (modular, mirroring the functional modules of the spec)
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "apps.common",
    "apps.users",
    "apps.courses",
    "apps.learning",
    "apps.assessments",
    "apps.ai",
    "apps.commerce",
    "apps.payments",
    "apps.certificates",
    "apps.notifications",
    "apps.analytics",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
# SQLite for local development and CI; PostgreSQL in production.
# ---------------------------------------------------------------------------
if os.environ.get("ORBITE_DB", "postgres") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("ORBITE_DB_NAME", "orbite"),
            "USER": os.environ.get("ORBITE_DB_USER", "orbite"),
            "PASSWORD": os.environ.get("ORBITE_DB_PASSWORD", ""),
            "HOST": os.environ.get("ORBITE_DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("ORBITE_DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("ORBITE_DB_NAME", BASE_DIR / "orbite.sqlite3"),
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Auth & users
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LOGIN_URL = "/api/v1/auth/login/"

# ---------------------------------------------------------------------------
# Internationalisation — French is the launch language, architecture is i18n-ready
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr"
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
    ("bm", "Bamanankan"),
    ("wo", "Wolof"),
]
TIME_ZONE = "Africa/Bamako"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# Video/files metadata only in Django; actual files live in a storage service.
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Built React app (frontend/dist) collected into STATIC_ROOT by Whitenoise.
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
STATICFILES_DIRS = [FRONTEND_DIST]

# Serve the built SPA (logo, manifest, assets) directly at clean root URLs,
# while STATIC_ROOT stays under /static/ (Django admin etc.).
WHITENOISE_ROOT = FRONTEND_DIST

# Whitenoise compresses collected files (no hashing → PWA manifest/public names intact).
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.OrbitePagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "EXCEPTION_HANDLER": "apps.common.exceptions.orbite_exception_handler",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("ORBITE_JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("ORBITE_JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    # Clé de signature dédiée aux jetons (rotation = déconnexion de tous les utilisateurs).
    "SIGNING_KEY": os.environ.get("ORBITE_JWT_SIGNING_KEY") or SECRET_KEY,
}

# ---------------------------------------------------------------------------
# CORS — React frontend is a separate application, never a source of truth
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "ORBITE_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
]
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get("ORBITE_SECURE_SSL", "1") == "1"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Rate limiting for sensitive endpoints handled at gateway/infra level.

# ---------------------------------------------------------------------------
# Email (dev console by default; SMTP via env)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "ORBITE_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("ORBITE_FROM_EMAIL", "orbite@orbite.example")
EMAIL_HOST = os.environ.get("ORBITE_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("ORBITE_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("ORBITE_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("ORBITE_EMAIL_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("ORBITE_EMAIL_TLS", "1") == "1"

# ---------------------------------------------------------------------------
# ORBITE-specific business configuration
# ---------------------------------------------------------------------------
ORBITE_SITE_URL = os.environ.get("ORBITE_SITE_URL", "http://localhost:5173")
ORBITE_VERIFY_URL = os.environ.get("ORBITE_VERIFY_URL", "/verify/{certificate_id}")
# LLM provider used by the AI layer. The AI Orchestrator routes to it.
ORBITE_LLM_PROVIDER = os.environ.get("ORBITE_LLM_PROVIDER", "mock")
ORBITE_LLM_API_KEY = os.environ.get("ORBITE_LLM_API_KEY", "")
ORBITE_LLM_MODEL = os.environ.get("ORBITE_LLM_MODEL", "orbite-default")
ORBITE_LLM_BASE_URL = os.environ.get(
    "ORBITE_LLM_BASE_URL",
    "https://api.openai.com/v1",
)

# Payment providers are an abstraction; the provider implementation is
# activated through this variable (e.g. "orange_money" once validated).
ORBITE_PAYMENT_PROVIDER = os.environ.get("ORBITE_PAYMENT_PROVIDER", "manual")

# Certificate authority
CERTIFICATE_PREFIX = os.environ.get("ORBITE_CERT_PREFIX", "ORB")
CERTIFICATE_ISSUER = os.environ.get("ORBITE_CERT_ISSUER", "ORBITE by Kweb")

# Cache / tasks
CACHES = {
    "default": {
        "BACKEND": os.environ.get(
            "ORBITE_CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache"
        ),
        "LOCATION": os.environ.get("ORBITE_CACHE_LOCATION", "orbite-cache"),
    }
}

# Celery is used for async jobs in production (certificates, media, email).
CELERY_BROKER_URL = os.environ.get("ORBITE_CELERY_BROKER", "redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = os.environ.get("ORBITE_CELERY_EAGER", "1") == "1"