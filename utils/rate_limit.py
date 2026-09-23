"""
Lightweight cache-based rate limiting.

Uses Django's cache framework (Redis in production, local-memory in dev —
see settings.py), so it scales across multiple app workers without any
paid rate-limiting service or extra infrastructure.
"""
from django.core.cache import cache


def hit(key, limit, window_seconds):
    """
    Record a hit for `key` and return True if the caller is now OVER the
    limit (i.e. should be blocked). Uses a simple fixed-window counter.
    """
    try:
        count = cache.incr(key)
    except ValueError:
        # Key doesn't exist yet
        cache.set(key, 1, timeout=window_seconds)
        count = 1
    return count > limit


def reset(key):
    cache.delete(key)


def seconds_remaining(key, default=0):
    """Best-effort TTL lookup; returns `default` if the backend can't report it."""
    ttl = getattr(cache, "ttl", None)
    if callable(ttl):
        try:
            return cache.ttl(key) or default
        except Exception:
            return default
    return default
