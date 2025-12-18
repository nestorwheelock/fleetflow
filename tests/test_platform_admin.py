"""
Tests for platform admin functionality.
"""
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        email='admin@fleetflow.com',
        password='adminpass123'
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email='user@example.com',
        password='userpass123'
    )


@pytest.fixture
def platform_tenant(db, superuser):
    from apps.tenants.models import Tenant
    return Tenant.objects.create(
        name='Test Tenant',
        slug='test-tenant',
        owner=superuser,
        plan='professional',
        business_name='Test Business',
        business_email='test@business.com',
    )


class TestPlatformAdminAccess:
    """Tests for platform admin access control."""

    def test_superuser_can_access_dashboard(self, client, superuser):
        client.force_login(superuser)
        response = client.get('/admin-platform/')
        assert response.status_code == 200

    def test_regular_user_cannot_access_dashboard(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get('/admin-platform/')
        assert response.status_code in [302, 403]

    def test_anonymous_user_redirected_to_login(self, client):
        response = client.get('/admin-platform/')
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_superuser_can_access_tenant_list(self, client, superuser):
        client.force_login(superuser)
        response = client.get('/admin-platform/tenants/')
        assert response.status_code == 200

    def test_superuser_can_view_tenant_detail(self, client, superuser, platform_tenant):
        client.force_login(superuser)
        response = client.get(f'/admin-platform/tenants/{platform_tenant.id}/')
        assert response.status_code == 200


class TestTenantManagement:
    """Tests for tenant management functionality."""

    def test_tenant_list_shows_all_tenants(self, client, superuser, platform_tenant):
        client.force_login(superuser)
        response = client.get('/admin-platform/tenants/')
        assert response.status_code == 200
        assert platform_tenant.business_name in response.content.decode()

    def test_tenant_detail_shows_info(self, client, superuser, platform_tenant):
        client.force_login(superuser)
        response = client.get(f'/admin-platform/tenants/{platform_tenant.id}/')
        assert response.status_code == 200
        content = response.content.decode()
        assert platform_tenant.business_name in content

    def test_tenant_edit_form_accessible(self, client, superuser, platform_tenant):
        client.force_login(superuser)
        response = client.get(f'/admin-platform/tenants/{platform_tenant.id}/edit/')
        assert response.status_code == 200

    def test_tenant_suspend_works(self, client, superuser, platform_tenant):
        from apps.tenants.models import Tenant
        client.force_login(superuser)
        response = client.post(f'/admin-platform/tenants/{platform_tenant.id}/suspend/')
        platform_tenant.refresh_from_db()
        assert not platform_tenant.is_active

    def test_tenant_reactivate_works(self, client, superuser, platform_tenant):
        from apps.tenants.models import Tenant
        platform_tenant.is_active = False
        platform_tenant.save()
        client.force_login(superuser)
        response = client.post(f'/admin-platform/tenants/{platform_tenant.id}/reactivate/')
        platform_tenant.refresh_from_db()
        assert platform_tenant.is_active


class TestPlatformSettings:
    """Tests for platform-wide settings."""

    def test_settings_page_accessible(self, client, superuser):
        client.force_login(superuser)
        response = client.get('/admin-platform/settings/')
        assert response.status_code == 200

    def test_settings_can_be_updated(self, client, superuser):
        client.force_login(superuser)
        response = client.post('/admin-platform/settings/', {
            'require_email_verification': 'on',
            'allow_customer_registration': 'on',
        })
        assert response.status_code in [200, 302]


class TestImpersonation:
    """Tests for user impersonation functionality."""

    def test_impersonate_user_accessible(self, client, superuser, platform_tenant):
        from apps.tenants.models import TenantUser
        TenantUser.objects.create(
            tenant=platform_tenant,
            user=superuser,
            role='owner'
        )
        client.force_login(superuser)
        response = client.get(f'/admin-platform/tenants/{platform_tenant.id}/users/')
        assert response.status_code == 200

    def test_cannot_impersonate_superuser(self, client, superuser):
        from apps.tenants.models import Tenant, TenantUser
        other_superuser = User.objects.create_superuser(
            email='other_admin@fleetflow.com',
            password='otherpass123'
        )
        tenant = Tenant.objects.create(
            name='Other Tenant',
            slug='other-tenant',
            owner=other_superuser,
            plan='starter',
            business_name='Other Business',
            business_email='other@business.com',
        )
        TenantUser.objects.create(
            tenant=tenant,
            user=other_superuser,
            role='owner'
        )

        client.force_login(superuser)
        response = client.post(f'/admin-platform/impersonate/{other_superuser.id}/', {
            'reason': 'Testing'
        })
        # Should be blocked or show error
        assert response.status_code in [302, 403]

    def test_impersonation_creates_log(self, client, superuser, regular_user, platform_tenant):
        from apps.tenants.models import TenantUser
        from apps.platform_admin.models import ImpersonationLog

        TenantUser.objects.create(
            tenant=platform_tenant,
            user=regular_user,
            role='staff'
        )

        client.force_login(superuser)
        initial_count = ImpersonationLog.objects.count()

        response = client.post(f'/admin-platform/impersonate/{regular_user.id}/', {
            'reason': 'Support ticket #123'
        })

        final_count = ImpersonationLog.objects.count()
        assert final_count == initial_count + 1

    def test_end_impersonation_returns_to_platform_admin(self, client, superuser, regular_user, platform_tenant):
        from apps.tenants.models import TenantUser

        TenantUser.objects.create(
            tenant=platform_tenant,
            user=regular_user,
            role='staff'
        )

        client.force_login(superuser)
        client.post(f'/admin-platform/impersonate/{regular_user.id}/', {
            'reason': 'Support ticket #123'
        })

        response = client.get('/admin-platform/impersonate/end/')
        assert response.status_code == 302
