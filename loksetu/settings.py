import logging
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env(name, default=''):
    """Blank values (e.g. `SECRET_KEY=`) count as unset; stray CR/whitespace is stripped."""
    return os.environ.get(name, '').strip() or default


def env_bool(name, default=False):
    return env(name, str(default)).lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    return [v.strip() for v in env(name, default).split(',') if v.strip()]


# ---------------------------------------------------------------- core
# Secure by default: DEBUG is OFF unless explicitly enabled (set DEBUG=True in your local .env).
DEBUG = env_bool('DEBUG', False)
SECRET_KEY = env('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('SECRET_KEY must be set when DEBUG is off.')
    SECRET_KEY = 'dev-only-insecure-key'

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
_render_host = env('RENDER_EXTERNAL_HOSTNAME')  # set automatically on Render
if _render_host:
    ALLOWED_HOSTS.append(_render_host)
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'accounts', 'departments', 'complaints', 'schemes', 'news', 'emergency',
    'audit', 'notifications', 'core',
    'projects', 'funds', 'documents', 'reports', 'faq', 'support', 'dashboard',
    'gallery', 'reviews', 'jobs', 'appointments',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'django.template.context_processors.i18n',
        'core.context_processors.site',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------- database
if env('DATABASE_URL'):
    DATABASES = {'default': dj_database_url.parse(env('DATABASE_URL'), conn_max_age=600,
                                                  conn_health_checks=True)}
else:  # local development only; the file is not persistent on most hosts
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

# ---------------------------------------------------------------- auth
AUTH_USER_MODEL = 'accounts.User'
AUTH_PASSWORD_VALIDATORS = [{'NAME': f'django.contrib.auth.password_validation.{n}'} for n in (
    'UserAttributeSimilarityValidator', 'MinimumLengthValidator',
    'CommonPasswordValidator', 'NumericPasswordValidator')]
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'home'
PASSWORD_RESET_TIMEOUT = 60 * 60 * 3  # reset links valid for 3 hours

# ---------------------------------------------------------------- i18n / static / media
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
LANGUAGES = [('en', 'English'), ('mr', 'मराठी')]
LOCALE_PATHS = [BASE_DIR / 'locale']
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Uploaded evidence is private and is served only through an authorised view (never directly).
# On a host with an ephemeral disk, point MEDIA_ROOT at a persistent disk / volume.
MEDIA_URL = 'media/'
MEDIA_ROOT = Path(env('MEDIA_ROOT', str(BASE_DIR / 'media')))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG
                    else 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
WHITENOISE_MANIFEST_STRICT = False  # a missing manifest entry must not 500 a page
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o640

# ---------------------------------------------------------------- email
if env('EMAIL_HOST_USER'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(env('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_TIMEOUT = 10  # never let a slow SMTP server hang a web worker
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', env('EMAIL_HOST_USER', 'LOKSETU <noreply@loksetu.local>'))

# ---------------------------------------------------------------- site details (footer / contact page)
CONTACT_EMAIL = env('CONTACT_EMAIL', env('EMAIL_HOST_USER'))
SOCIAL_LINKS = {k: env(f'{k.upper()}_URL') for k in ('linkedin', 'portfolio', 'github', 'instagram')}

# ---------------------------------------------------------------- throttling (see core/throttle.py)
# Number of reverse proxies in front of the app (Render/Heroku = 1). 0 = trust REMOTE_ADDR only.
NUM_PROXIES = int(env('NUM_PROXIES', '1' if not DEBUG else '0'))
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

# ---------------------------------------------------------------- security
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    SECURE_REDIRECT_EXEMPT = [r'^healthz/$']
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ---------------------------------------------------------------- logging / monitoring
LOGGING = {
    'version': 1, 'disable_existing_loggers': False,
    'formatters': {'std': {'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'}},
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'std'}},
    'root': {'handlers': ['console'], 'level': env('LOG_LEVEL', 'INFO')},
}
if env('SENTRY_DSN'):
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=env('SENTRY_DSN'), send_default_pii=False, traces_sample_rate=0.0)
    except ImportError:
        logging.getLogger(__name__).warning('SENTRY_DSN is set but sentry-sdk is not installed.')
# HSTS preload is a permanent, deliberate opt-in for a domain; enable it yourself when ready.
SILENCED_SYSTEM_CHECKS = ['security.W021']
