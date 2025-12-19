"""
URL Integrity Tests

These tests ensure ALL URLs in the application are valid and accessible.
This catches:
- Missing URL patterns
- Broken redirects
- Template errors
- Misconfigured views
"""
import pytest
from django.test import Client
from django.urls import get_resolver, reverse, NoReverseMatch
from django.conf import settings

from apps.tenants.models import User, Tenant, TenantUser


def get_all_url_names():
    """Extract all named URL patterns from the project."""
    resolver = get_resolver()
    url_names = set()

    def extract_names(patterns, namespace=''):
        for pattern in patterns:
            if hasattr(pattern, 'name') and pattern.name:
                full_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
                url_names.add(full_name)
            if hasattr(pattern, 'url_patterns'):
                ns = pattern.namespace or namespace
                extract_names(pattern.url_patterns, ns)

    extract_names(resolver.url_patterns)
    return url_names


class TestAllURLsResolve:
    """Test that all named URLs can be resolved."""

    @pytest.fixture
    def all_url_names(self):
        return get_all_url_names()

    def test_critical_auth_urls_exist(self, db):
        """Critical authentication URLs must exist."""
        critical_urls = [
            'login',
            'logout',
            'password_reset',
            'password_reset_done',
            'password_reset_complete',
        ]

        for url_name in critical_urls:
            try:
                url = reverse(url_name)
                assert url, f"URL '{url_name}' resolved to empty string"
            except NoReverseMatch:
                pytest.fail(f"Critical auth URL '{url_name}' does not exist!")

    def test_critical_tenant_urls_exist(self, db):
        """Critical tenant-related URLs must exist."""
        critical_urls = [
            'no-tenant',
            'dashboard-home',
        ]

        for url_name in critical_urls:
            try:
                url = reverse(url_name)
                assert url, f"URL '{url_name}' resolved to empty string"
            except NoReverseMatch:
                pytest.fail(f"Critical tenant URL '{url_name}' does not exist!")

    def test_platform_admin_urls_exist(self, db):
        """Platform admin URLs must exist."""
        critical_urls = [
            'platform_admin:dashboard',
            'platform_admin:tenant_list',
            'platform_admin:settings',
            'platform_admin:audit_logs',
        ]

        for url_name in critical_urls:
            try:
                url = reverse(url_name)
                assert url, f"URL '{url_name}' resolved to empty string"
            except NoReverseMatch:
                pytest.fail(f"Platform admin URL '{url_name}' does not exist!")


class TestMiddlewareRedirectURLsExist:
    """
    Test that all URLs used in middleware redirects actually exist.

    This is critical because middleware redirects happen before
    view processing, so broken redirect URLs cause 404s.
    """

    def test_tenant_required_middleware_redirect_exists(self, db):
        """The URL used by TenantRequiredMiddleware must exist."""
        # This is the exact check for the bug we found
        try:
            url = reverse('no-tenant')
            assert url == '/no-tenant/'
        except NoReverseMatch:
            pytest.fail(
                "TenantRequiredMiddleware redirects to 'no-tenant' "
                "but that URL name doesn't exist!"
            )

    def test_login_redirect_url_exists(self, db):
        """LOGIN_REDIRECT_URL must point to a valid URL."""
        redirect_url = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

        client = Client()
        response = client.get(redirect_url)

        # Allow redirect (302) or success (200) or auth required (login redirect)
        assert response.status_code in [200, 302], \
            f"LOGIN_REDIRECT_URL '{redirect_url}' returned {response.status_code}"

    def test_logout_redirect_url_exists(self, db):
        """LOGOUT_REDIRECT_URL must point to a valid URL if set."""
        redirect_url = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

        if redirect_url:
            client = Client()
            response = client.get(redirect_url)

            assert response.status_code in [200, 302], \
                f"LOGOUT_REDIRECT_URL '{redirect_url}' returned {response.status_code}"


class TestURLAccessibility:
    """Test that URLs return valid responses (not 500 errors)."""

    @pytest.fixture
    def superuser(self, db):
        return User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123'
        )

    @pytest.fixture
    def tenant_with_owner(self, db):
        user = User.objects.create_user(
            email='owner@test.com',
            password='ownerpass123'
        )
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=user,
            plan='professional',
            business_name='Test Business',
            business_email='test@test.com',
        )
        TenantUser.objects.create(
            tenant=tenant,
            user=user,
            role='owner',
            is_active=True
        )
        return tenant, user

    def test_public_urls_dont_500(self, client, db):
        """Public URLs should not return 500."""
        public_urls = [
            '/login/',
            '/no-tenant/',
        ]

        for url in public_urls:
            response = client.get(url)
            assert response.status_code != 500, \
                f"URL {url} returned 500 error"

    def test_platform_admin_urls_dont_500(self, client, superuser):
        """Platform admin URLs should not return 500."""
        client.login(username='admin@test.com', password='adminpass123')

        admin_urls = [
            '/admin-platform/',
            '/admin-platform/tenants/',
            '/admin-platform/settings/',
            '/admin-platform/audit-logs/',
        ]

        for url in admin_urls:
            response = client.get(url)
            assert response.status_code != 500, \
                f"Platform admin URL {url} returned 500 error"

    def test_dashboard_urls_dont_500(self, client, tenant_with_owner):
        """Dashboard URLs should not return 500."""
        tenant, user = tenant_with_owner
        client.login(username='owner@test.com', password='ownerpass123')

        dashboard_urls = [
            '/dashboard/',
            '/vehicles/',
            '/customers/',
            '/reservations/',
            '/settings/',
        ]

        for url in dashboard_urls:
            response = client.get(url, follow=True)
            assert response.status_code != 500, \
                f"Dashboard URL {url} returned 500 error"


class TestRedirectChainIntegrity:
    """Test that redirect chains end at valid destinations."""

    @pytest.fixture
    def superuser(self, db):
        return User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123'
        )

    def test_login_redirect_chain_valid(self, client, superuser):
        """Login redirect chain should end at valid page."""
        response = client.post('/login/', {
            'username': 'admin@test.com',
            'password': 'adminpass123',
        }, follow=True)

        assert response.status_code == 200, \
            f"Login redirect chain ended with {response.status_code}"

        # Check we didn't hit any 404s in the chain
        for redirect_url, status_code in response.redirect_chain:
            assert status_code != 404, \
                f"Redirect chain hit 404 at {redirect_url}"

    def test_logout_redirect_chain_valid(self, client, superuser):
        """Logout redirect chain should end at valid page."""
        client.login(username='admin@test.com', password='adminpass123')

        # Django 5+ requires POST for logout
        response = client.post('/logout/', follow=True)

        assert response.status_code == 200, \
            f"Logout redirect chain ended with {response.status_code}"


class TestTemplateRendering:
    """Test that templates render without errors."""

    @pytest.fixture
    def superuser(self, db):
        return User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123'
        )

    def test_no_tenant_template_renders(self, client, db):
        """No-tenant template should render."""
        user = User.objects.create_user(
            email='orphan@test.com',
            password='orphanpass123'
        )
        client.login(username='orphan@test.com', password='orphanpass123')

        response = client.get('/no-tenant/')

        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.content or b'<html' in response.content

    def test_login_template_renders(self, client, db):
        """Login template should render."""
        response = client.get('/login/')

        assert response.status_code == 200
        assert b'<form' in response.content

    def test_platform_admin_templates_render(self, client, superuser):
        """Platform admin templates should render."""
        client.login(username='admin@test.com', password='adminpass123')

        urls_to_test = [
            '/admin-platform/',
            '/admin-platform/tenants/',
            '/admin-platform/settings/',
            '/admin-platform/audit-logs/',
        ]

        for url in urls_to_test:
            response = client.get(url)
            assert response.status_code == 200, f"Template at {url} failed"
            assert b'<!DOCTYPE html>' in response.content or b'<html' in response.content, \
                f"Template at {url} doesn't look like HTML"
