"""
Tests for tenant branding functionality.
"""
import pytest
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def branding_tenant(db):
    from apps.tenants.models import Tenant
    owner = User.objects.create_user(
        email='owner@branding.com',
        password='ownerpass123'
    )
    return Tenant.objects.create(
        name='Branded Rentals',
        slug='branded-rentals',
        owner=owner,
        plan='professional',
        business_name='Branded Car Rentals',
        business_email='info@branded.com',
        is_active=True
    )


@pytest.fixture
def tenant_owner(db, branding_tenant):
    from apps.tenants.models import TenantUser
    return TenantUser.objects.create(
        tenant=branding_tenant,
        user=branding_tenant.owner,
        role='owner'
    )


class TestTenantBranding:
    """Tests for tenant branding model and functionality."""

    def test_get_or_create_branding(self, branding_tenant):
        from apps.tenants.models import TenantBranding

        branding = TenantBranding.get_or_create_for_tenant(branding_tenant)
        assert branding.tenant == branding_tenant
        assert branding.primary_color == '#3B82F6'  # Default

    def test_branding_css_generation(self, branding_tenant):
        from apps.tenants.models import TenantBranding

        branding = TenantBranding.objects.create(
            tenant=branding_tenant,
            primary_color='#FF0000',
            secondary_color='#00FF00',
            accent_color='#0000FF'
        )

        css = branding.get_css_variables()
        assert '--brand-primary: #FF0000' in css
        assert '--brand-secondary: #00FF00' in css
        assert '--brand-accent: #0000FF' in css

    def test_branding_settings_requires_owner(self, client, branding_tenant, tenant_owner):
        from apps.tenants.models import TenantUser

        staff_user = User.objects.create_user(
            email='staff@branding.com',
            password='staffpass123'
        )
        TenantUser.objects.create(
            tenant=branding_tenant,
            user=staff_user,
            role='staff'
        )

        client.force_login(staff_user)
        response = client.get('/dashboard/settings/branding/')
        assert response.status_code == 302  # Redirected due to not being owner

    def test_owner_can_access_branding_settings(self, client, branding_tenant, tenant_owner):
        client.force_login(branding_tenant.owner)
        response = client.get('/dashboard/settings/branding/')
        assert response.status_code == 200

    def test_owner_can_update_branding(self, client, branding_tenant, tenant_owner):
        from apps.tenants.models import TenantBranding

        TenantBranding.get_or_create_for_tenant(branding_tenant)

        client.force_login(branding_tenant.owner)
        response = client.post('/dashboard/settings/branding/', {
            'primary_color': '#123456',
            'secondary_color': '#654321',
            'accent_color': '#ABCDEF',
            'text_color': '#000000',
            'background_color': '#FFFFFF',
            'tagline': 'New Tagline',
            'welcome_message': 'Welcome!',
        })

        branding = TenantBranding.objects.get(tenant=branding_tenant)
        assert branding.primary_color == '#123456'
        assert branding.tagline == 'New Tagline'


class TestDomainSettings:
    """Tests for custom domain settings."""

    def test_domain_settings_requires_owner(self, client, branding_tenant, tenant_owner):
        from apps.tenants.models import TenantUser

        staff_user = User.objects.create_user(
            email='staff2@branding.com',
            password='staffpass123'
        )
        TenantUser.objects.create(
            tenant=branding_tenant,
            user=staff_user,
            role='staff'
        )

        client.force_login(staff_user)
        response = client.get('/dashboard/settings/domains/')
        assert response.status_code == 302

    def test_owner_can_access_domain_settings(self, client, branding_tenant, tenant_owner):
        client.force_login(branding_tenant.owner)
        response = client.get('/dashboard/settings/domains/')
        assert response.status_code == 200

    def test_owner_can_add_domain(self, client, branding_tenant, tenant_owner):
        from apps.tenants.models import TenantDomain

        client.force_login(branding_tenant.owner)
        response = client.post('/dashboard/settings/domains/', {
            'domain': 'custom.example.com'
        })

        domain = TenantDomain.objects.get(tenant=branding_tenant)
        assert domain.domain == 'custom.example.com'
        assert domain.verification_status == 'pending'
        assert domain.verification_token is not None

    def test_duplicate_domain_prevented(self, client, branding_tenant, tenant_owner):
        from apps.tenants.models import TenantDomain

        TenantDomain.objects.create(
            tenant=branding_tenant,
            domain='taken.example.com',
            verification_status='verified'
        )

        other_tenant = branding_tenant.__class__.objects.create(
            name='Other Tenant',
            slug='other-tenant',
            owner=User.objects.create_user(
                email='other@example.com',
                password='otherpass123'
            ),
            plan='starter',
            business_name='Other Business',
            business_email='other@business.com',
        )
        other_owner = other_tenant.owner
        from apps.tenants.models import TenantUser
        TenantUser.objects.create(
            tenant=other_tenant,
            user=other_owner,
            role='owner'
        )

        client.force_login(other_owner)
        response = client.post('/dashboard/settings/domains/', {
            'domain': 'taken.example.com'  # Already taken
        })

        # Should show error message
        assert TenantDomain.objects.filter(tenant=other_tenant).count() == 0
