from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden


def role_required(allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    Raises PermissionDenied if the user is not authenticated or lacks required role.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required.")

            try:
                profile = request.user.userprofile
            except AttributeError:
                raise PermissionDenied("User profile does not exist.")

            if profile.role not in allowed_roles:
                raise PermissionDenied("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
