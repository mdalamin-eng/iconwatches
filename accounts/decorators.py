from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """Restrict a view to users whose .role is in allowed_roles.
    Usage: @role_required("admin", "manager")
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied("You do not have access to this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# Convenience shortcuts
admin_required = role_required("admin")
staff_required = role_required("admin", "manager")  # admin OR manager
