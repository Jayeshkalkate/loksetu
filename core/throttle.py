"""Small cache-based rate limiter (per-process with the default local-memory cache)."""
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


def client_ip(request):
    n = settings.NUM_PROXIES
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if n and xff:
        parts = [p.strip() for p in xff.split(',') if p.strip()]
        if len(parts) >= n:
            return parts[-n]  # the address added by our own proxy; not client-spoofable
    return request.META.get('REMOTE_ADDR', 'unknown')


def hit(key, limit, window):
    """Count one hit; return True if the caller is still within the limit."""
    key = f'throttle:{key}'
    cache.add(key, 0, window)
    try:
        return cache.incr(key) <= limit
    except ValueError:  # key expired between add and incr
        cache.set(key, 1, window)
        return True


def throttle(name, limit, window, methods=('POST',), per_user=False):
    """View decorator: answer 429 once `limit` requests per `window` seconds are exceeded."""
    def deco(view):
        @wraps(view)
        def wrapper(request, *a, **k):
            if request.method in methods:
                who = f'u{request.user.pk}' if per_user and request.user.is_authenticated else client_ip(request)
                if not hit(f'{name}:{who}', limit, window):
                    return HttpResponse('Too many requests. Please wait a few minutes and try again.',
                                        status=429, content_type='text/plain')
            return view(request, *a, **k)
        return wrapper
    return deco
