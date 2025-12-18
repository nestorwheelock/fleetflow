import pytest
import tempfile
import shutil
from datetime import date
from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def temp_media_root(settings, tmp_path):
    """Use a temporary directory for media files during tests."""
    settings.MEDIA_ROOT = tmp_path / 'media'
    settings.MEDIA_ROOT.mkdir(exist_ok=True)
    yield settings.MEDIA_ROOT
    if settings.MEDIA_ROOT.exists():
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


class TenantAPIClient(APIClient):
    def __init__(self, tenant=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant = tenant

    def generic(self, method, path, *args, **kwargs):
        response = super().generic(method, path, *args, **kwargs)
        return response

    def request(self, **kwargs):
        request = super().request(**kwargs)
        return request


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def tenant(db, user):
    from apps.tenants.models import Tenant
    return Tenant.objects.create(
        name='Test Rental Co',
        slug='test-rental',
        owner=user,
        plan='professional',
        business_name='Test Rental Company',
        business_email='info@testrental.com',
        business_phone='555-0100',
        business_address='123 Test St, Test City, TX 75001',
        vehicle_limit=25,
        user_limit=3,
    )


@pytest.fixture
def tenant_user(db, tenant, user):
    from apps.tenants.models import TenantUser
    return TenantUser.objects.create(
        tenant=tenant,
        user=user,
        role='owner'
    )


@pytest.fixture
def tenant_client(api_client, tenant, tenant_user):
    api_client.force_authenticate(user=tenant_user.user)
    api_client.tenant = tenant
    api_client.tenant_user = tenant_user
    return api_client, tenant


@pytest.fixture
def vehicle(db, tenant):
    from apps.fleet.models import Vehicle
    return Vehicle.objects.create(
        tenant=tenant,
        make='Toyota',
        model='Camry',
        year=2023,
        license_plate='ABC123',
        vin='1HGBH41JXMN109186',
        color='Silver',
        status='available',
        daily_rate=50.00,
        mileage=15000,
    )


@pytest.fixture
def customer(db, tenant):
    from apps.customers.models import Customer
    return Customer.objects.create(
        tenant=tenant,
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='555-0101',
        address='456 Customer Ave, Test City, TX 75002',
        license_number='DL12345678',
        license_state='TX',
        license_expiry=date(2025, 12, 31),
        date_of_birth=date(1985, 5, 15),
    )


@pytest.fixture
def reservation(db, tenant, vehicle, customer):
    from apps.reservations.models import Reservation
    from datetime import timedelta
    from decimal import Decimal
    return Reservation.objects.create(
        tenant=tenant,
        vehicle=vehicle,
        customer=customer,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
        status='confirmed',
        daily_rate=Decimal('50.00'),
        total_amount=Decimal('100.00'),
    )
