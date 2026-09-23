"""
Thread-local storage for request and user objects.
Used by audit signals to capture context without passing parameters.
"""
from threading import local

_thread_local = local()


def set_current_user(user):
    """Store the current user in thread-local."""
    _thread_local.user = user


def get_current_user():
    """Retrieve the current user from thread-local."""
    return getattr(_thread_local, "user", None)


def set_current_request(request):
    """Store the current request in thread-local."""
    _thread_local.request = request


def get_current_request():
    """Retrieve the current request from thread-local."""
    return getattr(_thread_local, "request", None)