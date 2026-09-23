from .threadlocal import set_current_user, set_current_request


class AuditMiddleware:
    """
    Middleware to store the current user and request in thread-local storage
    so that audit signals can access them without explicit passing.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request and user in thread-local
        set_current_request(request)
        if request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)

        response = self.get_response(request)

        # Clean up thread-local to avoid memory leaks
        set_current_request(None)
        set_current_user(None)

        return response