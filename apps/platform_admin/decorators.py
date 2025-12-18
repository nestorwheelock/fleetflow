"""
Decorators for platform admin access control.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def superuser_required(view_func=None, login_url='/login/', raise_exception=False):
    """
    Decorator for views that checks that the user is a superuser.

    Usage:
        @superuser_required
        def my_view(request):
            ...

        @superuser_required(login_url='/admin/login/')
        def my_view(request):
            ...
    """
    def check_superuser(user):
        if not user.is_authenticated:
            return False
        if not user.is_superuser:
            if raise_exception:
                raise PermissionDenied("You do not have permission to access this page.")
            return False
        return True

    actual_decorator = user_passes_test(
        check_superuser,
        login_url=login_url,
    )

    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def platform_admin_required(view_func):
    """
    Decorator that requires the user to be a superuser.

    Redirects to login with an error message if not authorized.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')

        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access the platform admin.')
            return redirect('dashboard-home')

        return view_func(request, *args, **kwargs)
    return wrapper


class SuperuserRequiredMixin:
    """
    Mixin for class-based views that require superuser access.

    Usage:
        class MyView(SuperuserRequiredMixin, View):
            ...
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')

        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard-home')

        return super().dispatch(request, *args, **kwargs)
