"""
Tests for subdomain routing and custom domain functionality.
"""
import pytest
from django.test import Client, RequestFactory, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def subdomain_tenant(db):
    from apps.tenants.models import Tenant
    owner = User.objects.create_user(
        email='owner@example.com',
        password='ownerpass123'
    )
    return Tenant.objects.create(
        name='Rons Rentals',
        slug='ronsrentals',
        owner=owner,
        plan='professional',
        business_name='Rons Car Rentals',
        business_email='info@ronsrentals.com',
        is_active=True
    )


@pytest.fixture
def custom_domain(db, subdomain_tenant):
    from apps.tenants.models import TenantDomain
    return TenantDomain.objects.create(
        tenant=subdomain_tenant,
        domain='rentals.ronscompany.com',
        verification_status='verified',
        is_primary=False
    )


class TestSubdomainMiddleware:
    """Tests for SubdomainTenantMiddleware."""

    def test_subdomain_resolves_to_tenant(self, subdomain_tenant):
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/')
        request.META['HTTP_HOST'] = 'ronsrentals.localhost'
        request.META['SERVER_NAME'] = 'ronsrentals.localhost'

        response = middleware(request)
        assert hasattr(request, 'tenant')
        assert request.tenant == subdomain_tenant
        assert request.tenant_from_subdomain is True

    def test_invalid_subdomain_returns_404(self, subdomain_tenant):
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/')
        request.META['HTTP_HOST'] = 'nonexistent.localhost'
        request.META['SERVER_NAME'] = 'nonexistent.localhost'

        response = middleware(request)
        assert response.status_code == 404

    def test_www_subdomain_redirects(self, db):
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/')
        request.META['HTTP_HOST'] = 'www.fleetflow.com'
        request.META['SERVER_NAME'] = 'www.fleetflow.com'

        with override_settings(BASE_DOMAIN='fleetflow.com'):
            middleware.base_domain = 'fleetflow.com'
            response = middleware(request)

        assert response.status_code == 302
        assert 'www' not in response.url or '://www.' not in response.url

    def test_main_domain_has_no_tenant(self, db):
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/')
        request.META['HTTP_HOST'] = 'localhost'
        request.META['SERVER_NAME'] = 'localhost'

        response = middleware(request)
        assert request.tenant is None

    def test_exempt_paths_bypass_routing(self, subdomain_tenant):
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/static/css/style.css')
        request.META['HTTP_HOST'] = 'ronsrentals.localhost'
        request.META['SERVER_NAME'] = 'ronsrentals.localhost'

        response = middleware(request)
        assert response.status_code == 200
        assert request.tenant is None


class TestCustomDomainRouting:
    """Tests for custom domain resolution."""

    def test_custom_domain_resolves_to_tenant(self, subdomain_tenant, custom_domain):
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/')
        request.META['HTTP_HOST'] = 'rentals.ronscompany.com'
        request.META['SERVER_NAME'] = 'rentals.ronscompany.com'

        with override_settings(BASE_DOMAIN='fleetflow.com'):
            middleware.base_domain = 'fleetflow.com'
            response = middleware(request)

        assert request.tenant == subdomain_tenant
        assert request.tenant_from_custom_domain is True
        assert request.custom_domain == 'rentals.ronscompany.com'

    def test_unverified_domain_does_not_resolve(self, subdomain_tenant):
        from apps.tenants.models import TenantDomain
        from apps.tenants.middleware import SubdomainTenantMiddleware
        from django.http import HttpResponse

        unverified = TenantDomain.objects.create(
            tenant=subdomain_tenant,
            domain='pending.example.com',
            verification_status='pending'
        )

        def get_response(request):
            return HttpResponse('OK')

        middleware = SubdomainTenantMiddleware(get_response)
        factory = RequestFactory()

        request = factory.get('/')
        request.META['HTTP_HOST'] = 'pending.example.com'
        request.META['SERVER_NAME'] = 'pending.example.com'

        with override_settings(BASE_DOMAIN='fleetflow.com'):
            middleware.base_domain = 'fleetflow.com'
            response = middleware(request)

        assert request.tenant is None


class TestTenantDomainModel:
    """Tests for TenantDomain model."""

    def test_create_domain(self, subdomain_tenant):
        from apps.tenants.models import TenantDomain

        domain = TenantDomain.objects.create(
            tenant=subdomain_tenant,
            domain='newdomain.example.com',
            verification_status='pending',
            verification_token='test-token-123'
        )

        assert domain.domain == 'newdomain.example.com'
        assert domain.verification_status == 'pending'
        assert domain.verification_token == 'test-token-123'
        assert domain.ssl_provisioned is False

    def test_domain_uniqueness(self, subdomain_tenant, custom_domain):
        from apps.tenants.models import TenantDomain
        from django.db import IntegrityError

        with pytest.raises(IntegrityError):
            TenantDomain.objects.create(
                tenant=subdomain_tenant,
                domain='rentals.ronscompany.com',  # Already exists
                verification_status='pending'
            )

    def test_verified_domain_has_verified_at(self, subdomain_tenant):
        from apps.tenants.models import TenantDomain
        from django.utils import timezone

        domain = TenantDomain.objects.create(
            tenant=subdomain_tenant,
            domain='verified.example.com',
            verification_status='verified',
            verified_at=timezone.now()
        )

        assert domain.verified_at is not None
