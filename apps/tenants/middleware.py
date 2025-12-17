from django.shortcuts import redirect
from django.urls import reverse

from .models import TenantUser


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        request.tenant_user = None

        if request.user.is_authenticated:
            tenant_user = TenantUser.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('tenant').first()

            if tenant_user:
                request.tenant = tenant_user.tenant
                request.tenant_user = tenant_user

        response = self.get_response(request)
        return response


class TenantRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            '/admin/',
            '/api/auth/',
            '/login/',
            '/logout/',
            '/register/',
            '/static/',
            '/media/',
            '/__debug__/',
        ]

    def __call__(self, request):
        if request.user.is_authenticated:
            if not hasattr(request, 'tenant') or not request.tenant:
                path = request.path
                if not any(path.startswith(exempt) for exempt in self.exempt_paths):
                    if path.startswith('/dashboard/') or path.startswith('/api/'):
                        return redirect('/no-tenant/')

        response = self.get_response(request)
        return response
