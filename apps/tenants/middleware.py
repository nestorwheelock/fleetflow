from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Tenant, TenantUser, TenantDomain


class SubdomainTenantMiddleware:
    """
    Detect subdomain or custom domain and set request.tenant.

    Subdomain routing:
    - ronsrentals.fleetflow.com → Tenant(slug='ronsrentals')
    - www.fleetflow.com → redirect to fleetflow.com
    - fleetflow.com → request.tenant = None (marketing/platform site)
    - invalid.fleetflow.com → Show tenant not found page

    Custom domain routing:
    - rentals.mycompany.com → Tenant via TenantDomain(domain='rentals.mycompany.com')
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.base_domain = getattr(settings, 'BASE_DOMAIN', 'localhost')
        self.exempt_paths = [
            '/django-admin/',
            '/admin-platform/',
            '/static/',
            '/media/',
            '/__debug__/',
        ]

    def __call__(self, request):
        request.tenant = None
        request.tenant_from_subdomain = False
        request.tenant_from_custom_domain = False
        request.subdomain = None
        request.custom_domain = None

        host = request.get_host().split(':')[0].lower()

        if self._is_exempt_path(request.path):
            return self.get_response(request)

        subdomain = self._extract_subdomain(host)

        if subdomain == 'www':
            redirect_url = request.build_absolute_uri().replace('://www.', '://', 1)
            return HttpResponseRedirect(redirect_url)

        if subdomain:
            request.subdomain = subdomain
            try:
                tenant = Tenant.objects.get(slug=subdomain, is_active=True)
                request.tenant = tenant
                request.tenant_from_subdomain = True
            except Tenant.DoesNotExist:
                if not request.path.startswith('/login/'):
                    return render(request, 'tenants/tenant_not_found.html', {
                        'subdomain': subdomain
                    }, status=404)
        else:
            tenant = self._resolve_custom_domain(host)
            if tenant:
                request.tenant = tenant
                request.tenant_from_custom_domain = True
                request.custom_domain = host

        return self.get_response(request)

    def _resolve_custom_domain(self, host):
        """Check if host is a verified custom domain and return the tenant."""
        try:
            tenant_domain = TenantDomain.objects.select_related('tenant').get(
                domain=host,
                verification_status='verified',
                tenant__is_active=True
            )
            return tenant_domain.tenant
        except TenantDomain.DoesNotExist:
            return None

    def _extract_subdomain(self, host):
        """Extract subdomain from host."""
        base_domain = self.base_domain.lower()

        if host == base_domain:
            return None

        if host == f'www.{base_domain}':
            return 'www'

        if host.endswith(f'.{base_domain}'):
            subdomain = host[:-len(f'.{base_domain}')]
            if subdomain:
                return subdomain

        if host in ('localhost', '127.0.0.1') or host.endswith('.localhost'):
            if host.endswith('.localhost'):
                subdomain = host[:-len('.localhost')]
                if subdomain:
                    return subdomain

        return None

    def _is_exempt_path(self, path):
        """Check if path is exempt from subdomain processing."""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)


class TenantMiddleware:
    """
    Set tenant user context and handle tenant selection.

    If SubdomainTenantMiddleware already set request.tenant (from subdomain),
    verify user has access to that tenant. Otherwise, select user's first tenant.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'tenant'):
            request.tenant = None
        request.tenant_user = None

        if request.user.is_authenticated:
            if getattr(request, 'tenant_from_subdomain', False) and request.tenant:
                tenant_user = TenantUser.objects.filter(
                    user=request.user,
                    tenant=request.tenant,
                    is_active=True
                ).select_related('tenant').first()

                if tenant_user:
                    request.tenant_user = tenant_user
                elif request.user.is_superuser:
                    request.tenant_user = None
                else:
                    request.tenant = None
            else:
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
            '/django-admin/',
            '/admin-platform/',
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
