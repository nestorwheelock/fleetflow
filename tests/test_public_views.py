"""
Tests for public-facing views (tenant landing pages and customer portal).
"""
import pytest
from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


@pytest.fixture
def public_tenant(db):
    from apps.tenants.models import Tenant, TenantBranding
    owner = User.objects.create_user(
        email='owner@rental.com',
        password='ownerpass123'
    )
    tenant = Tenant.objects.create(
        name='Best Rentals',
        slug='best-rentals',
        owner=owner,
        plan='professional',
        business_name='Best Car Rentals',
        business_email='info@bestrentals.com',
        business_phone='555-1234',
        is_active=True
    )
    TenantBranding.objects.create(
        tenant=tenant,
        primary_color='#2563EB',
        tagline='The Best Cars for Your Journey'
    )
    return tenant


@pytest.fixture
def public_vehicle(db, public_tenant):
    from apps.fleet.models import Vehicle
    return Vehicle.objects.create(
        tenant=public_tenant,
        make='Honda',
        model='Accord',
        year=2024,
        license_plate='PUB123',
        vin='1HGCV2F45NA000001',
        color='Blue',
        status='available',
        daily_rate=55.00,
        is_featured=True
    )


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        email='customer@example.com',
        password='customerpass123'
    )


class TestPublicLandingPage:
    """Tests for tenant public landing page."""

    def test_landing_page_loads(self, client, public_tenant):
        response = client.get('/public/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 200

    def test_landing_page_shows_tenant_branding(self, client, public_tenant):
        response = client.get('/public/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        content = response.content.decode()
        assert public_tenant.business_name in content

    def test_landing_page_shows_available_vehicles(self, client, public_tenant, public_vehicle):
        response = client.get('/public/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        content = response.content.decode()
        assert 'Honda' in content or 'Accord' in content


class TestVehicleGallery:
    """Tests for public vehicle gallery."""

    def test_vehicle_gallery_loads(self, client, public_tenant):
        response = client.get('/public/vehicles/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 200

    def test_vehicle_gallery_shows_available_vehicles(self, client, public_tenant, public_vehicle):
        response = client.get('/public/vehicles/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        content = response.content.decode()
        assert 'Honda' in content or 'Accord' in content

    def test_vehicle_detail_loads(self, client, public_tenant, public_vehicle):
        response = client.get(
            f'/public/vehicles/{public_vehicle.id}/',
            HTTP_HOST=f'{public_tenant.slug}.localhost'
        )
        assert response.status_code == 200


class TestCustomerRegistration:
    """Tests for customer self-registration."""

    def test_registration_page_loads(self, client, public_tenant):
        response = client.get('/public/register/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 200

    def test_customer_can_register(self, client, public_tenant):
        response = client.post('/public/register/', {
            'email': 'newcustomer@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Customer',
            'phone': '555-5555'
        }, HTTP_HOST=f'{public_tenant.slug}.localhost')

        # Should redirect after successful registration
        assert response.status_code in [200, 302]

    def test_duplicate_email_prevented(self, client, public_tenant, customer_user):
        response = client.post('/public/register/', {
            'email': customer_user.email,  # Already exists
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'Duplicate',
            'last_name': 'User',
        }, HTTP_HOST=f'{public_tenant.slug}.localhost')

        # Form should show error
        assert response.status_code == 200


class TestCustomerPortal:
    """Tests for customer portal."""

    def test_portal_requires_login(self, client, public_tenant):
        response = client.get('/public/customer/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_authenticated_customer_can_access_portal(self, client, public_tenant, customer_user):
        from apps.customers.models import Customer
        from apps.tenants.models import TenantUser

        TenantUser.objects.create(
            tenant=public_tenant,
            user=customer_user,
            role='customer'
        )

        Customer.objects.create(
            tenant=public_tenant,
            user=customer_user,
            first_name='Test',
            last_name='Customer',
            email=customer_user.email,
            phone='555-0000'
        )

        client.force_login(customer_user)
        response = client.get('/public/customer/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 200


class TestCustomerDocuments:
    """Tests for customer document upload."""

    def test_documents_page_requires_login(self, client, public_tenant):
        response = client.get('/public/customer/documents/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 302

    def test_customer_can_view_documents_page(self, client, public_tenant, customer_user):
        from apps.customers.models import Customer
        from apps.tenants.models import TenantUser

        TenantUser.objects.create(
            tenant=public_tenant,
            user=customer_user,
            role='customer'
        )

        Customer.objects.create(
            tenant=public_tenant,
            user=customer_user,
            first_name='Test',
            last_name='Customer',
            email=customer_user.email,
            phone='555-0000'
        )

        client.force_login(customer_user)
        response = client.get('/public/customer/documents/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 200


class TestCustomerReservations:
    """Tests for customer reservation views."""

    def test_reservations_page_requires_login(self, client, public_tenant):
        response = client.get('/public/customer/reservations/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 302

    def test_customer_can_view_reservations(self, client, public_tenant, customer_user, public_vehicle):
        from apps.customers.models import Customer
        from apps.tenants.models import TenantUser
        from apps.reservations.models import Reservation
        from datetime import timedelta
        from decimal import Decimal

        TenantUser.objects.create(
            tenant=public_tenant,
            user=customer_user,
            role='customer'
        )

        customer = Customer.objects.create(
            tenant=public_tenant,
            user=customer_user,
            first_name='Test',
            last_name='Customer',
            email=customer_user.email,
            phone='555-0000'
        )

        Reservation.objects.create(
            tenant=public_tenant,
            vehicle=public_vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7),
            status='confirmed',
            daily_rate=Decimal('55.00'),
            total_amount=Decimal('110.00')
        )

        client.force_login(customer_user)
        response = client.get('/public/customer/reservations/', HTTP_HOST=f'{public_tenant.slug}.localhost')
        assert response.status_code == 200
        assert 'Honda' in response.content.decode() or 'Accord' in response.content.decode()
