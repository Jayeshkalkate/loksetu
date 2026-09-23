import os
import logging
from pathlib import Path
from decouple import config
import dj_database_url
import cloudinary
from cryptography.fernet import Fernet

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECURITY & ENVIRONMENT
# --------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-key")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://*.onrender.com,http://localhost:8000"
).split(",")

# Symmetric key used to encrypt sensitive PII fields (Aadhaar numbers) at
# rest — see utils/encrypted_fields.py. Uses the free, open-source
# `cryptography` library; no paid KMS is required.
# Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
_field_key = config("FIELD_ENCRYPTION_KEY", default="")
if not _field_key:
    if DEBUG:
        # Deterministic-per-process dev fallback ONLY — never use this in
        # production. Data encrypted with this key is NOT portable between
        # runs, which is fine for local development but would be a bug in
        # any deployed environment.
        _field_key = Fernet.generate_key().decode()
        logging.getLogger(__name__).warning(
            "FIELD_ENCRYPTION_KEY is not set — using an ephemeral dev-only key. "
            "Set FIELD_ENCRYPTION_KEY in the environment before deploying."
        )
    else:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEY must be set in production. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
FIELD_ENCRYPTION_KEY = _field_key

# --------------------------------------------------
# APPLICATION DEFINITION
# --------------------------------------------------
INSTALLED_APPS = [
    # Django built‑ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third‑party
    "rest_framework",
    "django_filters",
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "account",
    "post",
    "complaint",
    "schemes",
    "funds",
    "audit",
    "documents",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",          # for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.AuditMiddleware",                    # custom audit
]

ROOT_URLCONF = "loksetu.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "loksetu.wsgi.application"

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC & MEDIA FILES
# --------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use Whitenoise for static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files.
# Cloudinary's free tier (25 GB storage / 25 GB bandwidth per month) is used
# in production so no paid object-storage service is required. If Cloudinary
# credentials are not supplied (e.g. running the free Render tier without a
# Cloudinary account yet), we fall back to local filesystem storage instead
# of crashing on startup.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")
USE_CLOUDINARY = not DEBUG and all(
    [CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]
)

if USE_CLOUDINARY:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
    }
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    STORAGES = {
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }

# --------------------------------------------------
# EMAIL CONFIGURATION
# --------------------------------------------------
# Gmail SMTP (free, 500 msgs/day) is the default transport — no paid email
# API (SendGrid/Mailgun/etc.) is required. If no credentials are configured
# (e.g. local development), emails are printed to the console instead of
# silently failing or requiring a paid provider.
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "noreply@loksetu.local"

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --------------------------------------------------
# CELERY
# --------------------------------------------------
# Redis (self-hosted or a free-tier managed instance such as Upstash/Render)
# is the broker — no paid queue service is required.
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=DEBUG, cast=bool)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# --------------------------------------------------
# CACHE (used for rate limiting — OTP, login lockout)
# --------------------------------------------------
# Uses Django's built-in Redis cache backend (core since Django 4.2, no
# extra package beyond the `redis` client already required for Celery) so
# rate-limit counters are shared correctly across multiple app workers —
# this is what makes the app horizontally scalable. Falls back to local
# in-process memory when Redis isn't configured (fine for a single dev
# worker, but won't share state across processes).
_redis_url = config("REDIS_URL", default="")
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_url,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# --------------------------------------------------
# OTP
# --------------------------------------------------
OTP_EXPIRY_SECONDS = config("OTP_EXPIRY_SECONDS", default=300, cast=int)

# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Free (no paid API-gateway needed) throttling using the cache above,
    # so the public API can't be trivially hammered.
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "300/min",
    },
}

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# Log out idle sessions after 2 hours instead of leaving them open forever.
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=60 * 60 * 2, cast=int)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --------------------------------------------------
# ERROR MONITORING (optional, free tier)
# --------------------------------------------------
# Sentry's free "Developer" tier (5k errors/month) is enough for a project
# this size. Only initializes if SENTRY_DSN is actually set, so it's a
# no-op — not a hard dependency — everywhere else.
SENTRY_DSN = config("SENTRY_DSN", default="")
if SENTRY_DSN and not DEBUG:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
    except ImportError:
        logging.getLogger(__name__).warning("SENTRY_DSN set but sentry-sdk is not installed.")

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "level": "DEBUG" if DEBUG else "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# --------------------------------------------------
# DEFAULT AUTO FIELD
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"