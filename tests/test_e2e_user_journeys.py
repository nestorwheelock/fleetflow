"""
End-to-End User Journey Tests

These tests simulate REAL user journeys through the application,
testing the full request/response cycle including:
- Login flows with redirects
- Middleware processing
- URL resolution
- Template rendering

These tests catch issues that isolated view tests miss.
"""
import pytest
from django.test import Client, override_settings
from django.urls import reverse, NoReverseMatch
from django.conf import settings

from apps.tenants.models import User, Tenant, TenantUser


@pytest.fixture
def superuser(db):
    """Create a superuser for testing."""
    return User.objects.create_superuser(
        email='admin@test.com',
        password='adminpass123'
    )


@pytest.fixture
def tenant_owner(db, tenant):
    """Create a tenant owner user."""
    user = User.objects.create_user(
        email='owner@tenant.com',
        password='ownerpass123'
    )
    TenantUser.objects.create(
        tenant=tenant,
        user=user,
        role='owner',
        is_active=True
    )
    return user


@pytest.fixture
def user_without_tenant(db):
    """Create a user with no tenant association."""
    return User.objects.create_user(
        email='orphan@test.com',
        password='orphanpass123'
    )


class TestAllRedirectsResolve:
    """
    Test that ALL redirects in the application point to valid URLs.

    This catches the /no-tenant/ bug where middleware redirected to
    a URL that didn't exist.
    """

    def test_no_tenant_url_exists(self, db):
        """The /no-tenant/ URL must exist."""
        client = Client()
        response = client.get('/no-tenant/')
        # Should redirect to login (requires auth) or return 200/302
        assert response.status_code in [200, 302], \
            f"/no-tenant/ returned {response.status_code}, expected 200 or 302"

    def test_all_named_urls_resolve(self, db):
        """All named URLs in the project should resolve."""
        critical_urls = [
            'login',
            'logout',
            'no-tenant',
            'dashboard-home',
            'platform_admin:dashboard',
            'platform_admin:tenant_list',
            'platform_admin:settings',
            'platform_admin:audit_logs',
        ]

        for url_name in critical_urls:
            try:
                url = reverse(url_name)
                assert url is not None, f"URL '{url_name}' returned None"
            except NoReverseMatch:
                pytest.fail(f"URL name '{url_name}' does not exist!")


class TestSuperuserLoginJourney:
    """
    Test the complete login journey for a superuser.

    This is the exact flow that was broken:
    1. Superuser visits /login/
    2. Submits credentials
    3. Gets redirected (should go to platform admin or dashboard)
    4. Final destination should be accessible (not 404)
    """

    def test_superuser_login_redirects_to_valid_page(self, client, superuser):
        """Superuser login should redirect to an accessible page."""
        # Step 1: POST login credentials
        response = client.post('/login/', {
            'username': 'admin@test.com',
            'password': 'adminpass123',
        }, follow=False)

        # Should redirect somewhere
        assert response.status_code == 302, \
            f"Login should redirect, got {response.status_code}"

        redirect_url = response.url

        # Step 2: Follow the redirect
        response = client.get(redirect_url, follow=True)

        # Final response should be 200, not 404
        assert response.status_code == 200, \
            f"After login, superuser landed on {redirect_url} which returned {response.status_code}"

    def test_superuser_can_access_platform_admin_after_login(self, client, superuser):
        """Superuser should be able to access platform admin after login."""
        # Login
        client.login(username='admin@test.com', password='adminpass123')

        # Access platform admin
        response = client.get('/admin-platform/')

        assert response.status_code == 200, \
            f"Platform admin returned {response.status_code}"

    def test_superuser_accessing_dashboard_without_tenant(self, client, superuser):
        """Superuser accessing /dashboard/ should not get 404."""
        client.login(username='admin@test.com', password='adminpass123')

        response = client.get('/dashboard/', follow=True)

        # Should either show dashboard or redirect to valid page
        assert response.status_code == 200, \
            f"Dashboard access returned {response.status_code}"


class TestTenantOwnerLoginJourney:
    """Test the complete login journey for a tenant owner."""

    def test_tenant_owner_login_redirects_to_dashboard(self, client, tenant_owner, tenant):
        """Tenant owner login should redirect to their dashboard."""
        response = client.post('/login/', {
            'username': 'owner@tenant.com',
            'password': 'ownerpass123',
        }, follow=True)

        assert response.status_code == 200, \
            f"Tenant owner login journey ended with {response.status_code}"

    def test_tenant_owner_can_access_dashboard(self, client, tenant_owner, tenant):
        """Tenant owner should access their dashboard successfully."""
        client.login(username='owner@tenant.com', password='ownerpass123')

        response = client.get('/dashboard/', follow=True)

        assert response.status_code == 200, \
            f"Dashboard returned {response.status_code}"


class TestUserWithoutTenantJourney:
    """Test journey for a user with no tenant association."""

    def test_user_without_tenant_redirected_properly(self, client, user_without_tenant):
        """User without tenant should be redirected to /no-tenant/."""
        client.login(username='orphan@test.com', password='orphanpass123')

        response = client.get('/dashboard/', follow=True)

        # Should end up on a valid page (no-tenant or similar)
        assert response.status_code == 200, \
            f"User without tenant ended at page with status {response.status_code}"

    def test_no_tenant_page_renders(self, client, user_without_tenant):
        """The no-tenant page should render correctly."""
        client.login(username='orphan@test.com', password='orphanpass123')

        response = client.get('/no-tenant/')

        assert response.status_code == 200, \
            f"/no-tenant/ returned {response.status_code}"

        # Check content
        content = response.content.decode()
        assert 'No Tenant Access' in content or 'no tenant' in content.lower(), \
            "No-tenant page should explain the situation"


class TestMiddlewareRedirectChains:
    """
    Test that middleware redirect chains always end at valid URLs.

    Middleware can chain redirects. We need to ensure the final
    destination is always valid.
    """

    def test_unauthenticated_dashboard_access(self, client, db):
        """Unauthenticated access to dashboard should redirect to login."""
        response = client.get('/dashboard/', follow=True)

        assert response.status_code == 200, \
            f"Unauthenticated dashboard access ended with {response.status_code}"

        # Should be on login page
        assert '/login/' in response.request['PATH_INFO'] or \
               'login' in response.content.decode().lower(), \
            "Should redirect to login page"

    def test_unauthenticated_platform_admin_access(self, client, db):
        """Unauthenticated access to platform admin should redirect to login."""
        response = client.get('/admin-platform/', follow=True)

        assert response.status_code == 200, \
            f"Unauthenticated platform admin access ended with {response.status_code}"


class TestCriticalPageRender:
    """
    Test that all critical pages actually render without errors.

    This catches template errors, missing context variables, etc.
    """

    def test_login_page_renders(self, client, db):
        """Login page should render."""
        response = client.get('/login/')

        assert response.status_code == 200
        assert b'<form' in response.content or b'<input' in response.content

    def test_platform_admin_dashboard_renders(self, client, superuser):
        """Platform admin dashboard should render with data."""
        client.login(username='admin@test.com', password='adminpass123')

        response = client.get('/admin-platform/')

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Dashboard' in content or 'dashboard' in content.lower()

    def test_platform_admin_tenant_list_renders(self, client, superuser, tenant):
        """Tenant list should render."""
        client.login(username='admin@test.com', password='adminpass123')

        response = client.get('/admin-platform/tenants/')

        assert response.status_code == 200

    def test_platform_admin_settings_renders(self, client, superuser):
        """Platform settings should render."""
        client.login(username='admin@test.com', password='adminpass123')

        response = client.get('/admin-platform/settings/')

        assert response.status_code == 200

    def test_tenant_dashboard_renders(self, client, tenant_owner, tenant):
        """Tenant dashboard should render."""
        client.login(username='owner@tenant.com', password='ownerpass123')

        response = client.get('/dashboard/', follow=True)

        assert response.status_code == 200


class TestErrorPagesDontCrash:
    """Test that error scenarios don't result in 500 errors."""

    def test_404_page_renders(self, client, db):
        """404 page should render, not crash."""
        response = client.get('/this-page-definitely-does-not-exist-xyz/')

        assert response.status_code == 404, \
            f"Expected 404, got {response.status_code}"

    def test_invalid_tenant_detail_404(self, client, superuser):
        """Invalid tenant ID should 404, not 500."""
        client.login(username='admin@test.com', password='adminpass123')

        response = client.get('/admin-platform/tenants/99999/')

        assert response.status_code == 404, \
            f"Invalid tenant should 404, got {response.status_code}"


class TestFormSubmissions:
    """Test that form submissions work correctly."""

    def test_login_form_submission(self, client, superuser):
        """Login form should process POST correctly."""
        response = client.post('/login/', {
            'username': 'admin@test.com',
            'password': 'adminpass123',
        })

        # Should redirect on success
        assert response.status_code == 302, \
            f"Login POST should redirect, got {response.status_code}"

    def test_login_form_with_bad_credentials(self, client, superuser):
        """Bad credentials should show error, not crash."""
        response = client.post('/login/', {
            'username': 'admin@test.com',
            'password': 'wrongpassword',
        })

        # Should re-render form with error
        assert response.status_code == 200, \
            f"Bad login should show form again, got {response.status_code}"


class TestSecurityRedirects:
    """Test security-related redirects work correctly."""

    def test_non_superuser_cannot_access_platform_admin(self, client, tenant_owner):
        """Non-superuser should be redirected from platform admin."""
        client.login(username='owner@tenant.com', password='ownerpass123')

        response = client.get('/admin-platform/', follow=True)

        # Should be redirected away, not given access
        assert response.status_code == 200
        # Should NOT be on platform admin
        assert '/admin-platform/' not in response.request['PATH_INFO']

    def test_logout_redirects_properly(self, client, superuser):
        """Logout should redirect to a valid page."""
        client.login(username='admin@test.com', password='adminpass123')

        # Django 5+ requires POST for logout
        response = client.post('/logout/', follow=True)

        assert response.status_code == 200, \
            f"Logout journey ended with {response.status_code}"
