from django.http import HttpResponseForbidden

def role_required(allowed_roles):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return HttpResponseForbidden("Login Required")

            profile = getattr(
                request.user,
                "userprofile",
                None
            )

            
            if not profile:
                return HttpResponseForbidden(
                    "Profile Missing"
                )
                
            role = profile.role

            if role not in allowed_roles:
                return HttpResponseForbidden("Permission Denied")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator