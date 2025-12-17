import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class TestTenantModel:
    def test_tenant_creation(self, db, user):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.create(
            name='Acme Rentals',
            slug='acme-rentals',
            owner=user,
            plan='starter',
            business_name='Acme Rental Company',
            business_email='info@acme.com',
            business_phone='555-1234',
            business_address='100 Main St',
            vehicle_limit=10,
            user_limit=1,
        )
        assert tenant.pk is not None
        assert tenant.name == 'Acme Rentals'
        assert tenant.slug == 'acme-rentals'
        assert tenant.is_active is True

    def test_tenant_slug_unique(self, db, user):
        from apps.tenants.models import Tenant
        Tenant.objects.create(
            name='First Rental',
            slug='unique-slug',
            owner=user,
            plan='starter',
            business_name='First',
            business_email='first@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        with pytest.raises(IntegrityError):
            Tenant.objects.create(
                name='Second Rental',
                slug='unique-slug',
                owner=user,
                plan='starter',
                business_name='Second',
                business_email='second@test.com',
                vehicle_limit=10,
                user_limit=1,
            )

    def test_tenant_str_representation(self, tenant):
        assert str(tenant) == 'Test Rental Co'

    def test_tenant_default_values(self, db, user):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.create(
            name='Default Test',
            slug='default-test',
            owner=user,
            plan='starter',
            business_name='Default Business',
            business_email='default@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        assert tenant.is_active is True
        assert tenant.currency == 'USD'
        assert tenant.timezone == 'America/Chicago'

    def test_tenant_trial_period(self, db, user):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.create(
            name='Trial Test',
            slug='trial-test',
            owner=user,
            plan='starter',
            business_name='Trial Business',
            business_email='trial@test.com',
            vehicle_limit=10,
            user_limit=1,
            trial_ends_at=timezone.now() + timedelta(days=14),
        )
        assert tenant.is_in_trial() is True

    def test_tenant_expired_trial(self, db, user):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.create(
            name='Expired Trial',
            slug='expired-trial',
            owner=user,
            plan='starter',
            business_name='Expired Business',
            business_email='expired@test.com',
            vehicle_limit=10,
            user_limit=1,
            trial_ends_at=timezone.now() - timedelta(days=1),
        )
        assert tenant.is_in_trial() is False

    def test_tenant_plan_limits(self, tenant):
        assert tenant.vehicle_limit == 25
        assert tenant.user_limit == 3

    def test_tenant_has_feature(self, tenant):
        assert tenant.has_feature('fleet') is True
        assert tenant.has_feature('online_booking') is True
        assert tenant.has_feature('gps') is False

    def test_tenant_can_add_vehicle(self, tenant):
        assert tenant.can_add_vehicle() is True

    def test_tenant_cannot_exceed_vehicle_limit(self, db, tenant):
        from apps.fleet.models import Vehicle
        for i in range(25):
            Vehicle.objects.create(
                tenant=tenant,
                make='Toyota',
                model=f'Model{i}',
                year=2023,
                license_plate=f'PLT{i:03d}',
                vin=f'VIN{i:017d}',
                status='available',
                daily_rate=50.00,
            )
        assert tenant.can_add_vehicle() is False


class TestTenantUserModel:
    def test_tenant_user_creation(self, db, tenant, user):
        from apps.tenants.models import TenantUser
        tenant_user = TenantUser.objects.create(
            tenant=tenant,
            user=user,
            role='staff'
        )
        assert tenant_user.pk is not None
        assert tenant_user.role == 'staff'

    def test_tenant_user_roles(self, db, tenant, user):
        from apps.tenants.models import TenantUser
        for role in ['owner', 'manager', 'staff']:
            tenant_user = TenantUser.objects.create(
                tenant=tenant,
                user=User.objects.create_user(
                    username=f'{role}user',
                    email=f'{role}@test.com',
                    password='test123'
                ),
                role=role
            )
            assert tenant_user.role == role

    def test_tenant_user_unique_together(self, db, tenant, user):
        from apps.tenants.models import TenantUser
        TenantUser.objects.create(tenant=tenant, user=user, role='owner')
        with pytest.raises(IntegrityError):
            TenantUser.objects.create(tenant=tenant, user=user, role='staff')

    def test_tenant_user_str_representation(self, tenant_user):
        expected = f'{tenant_user.user.username} @ {tenant_user.tenant.name}'
        assert str(tenant_user) == expected

    def test_tenant_user_is_owner(self, tenant_user):
        assert tenant_user.is_owner() is True

    def test_tenant_user_is_manager(self, db, tenant):
        from apps.tenants.models import TenantUser
        manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='test123'
        )
        tenant_user = TenantUser.objects.create(
            tenant=tenant,
            user=manager_user,
            role='manager'
        )
        assert tenant_user.is_manager() is True
        assert tenant_user.is_owner() is False

    def test_tenant_user_permissions_owner(self, tenant_user):
        assert tenant_user.can_manage_vehicles() is True
        assert tenant_user.can_manage_reservations() is True
        assert tenant_user.can_manage_users() is True

    def test_tenant_user_permissions_staff(self, db, tenant):
        from apps.tenants.models import TenantUser
        staff_user = User.objects.create_user(
            username='staffmember',
            email='staff@test.com',
            password='test123'
        )
        tenant_user = TenantUser.objects.create(
            tenant=tenant,
            user=staff_user,
            role='staff'
        )
        assert tenant_user.can_manage_vehicles() is True
        assert tenant_user.can_manage_reservations() is True
        assert tenant_user.can_manage_users() is False


class TestTenantAPI:
    def test_tenant_list_requires_auth(self, api_client):
        response = api_client.get('/api/tenants/')
        assert response.status_code == 403

    def test_tenant_list_authenticated(self, authenticated_client, tenant, tenant_user):
        response = authenticated_client.get('/api/tenants/')
        assert response.status_code == 200

    def test_tenant_detail(self, authenticated_client, tenant, tenant_user):
        response = authenticated_client.get(f'/api/tenants/{tenant.pk}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Test Rental Co'

    def test_tenant_update(self, authenticated_client, tenant, tenant_user):
        response = authenticated_client.patch(
            f'/api/tenants/{tenant.pk}/',
            {'business_name': 'Updated Business Name'}
        )
        assert response.status_code == 200
        tenant.refresh_from_db()
        assert tenant.business_name == 'Updated Business Name'

    def test_tenant_stats_endpoint(self, authenticated_client, tenant, tenant_user, vehicle):
        response = authenticated_client.get(f'/api/tenants/{tenant.pk}/stats/')
        assert response.status_code == 200
        assert 'vehicle_count' in response.data
        assert response.data['vehicle_count'] == 1


class TestTenantMiddleware:
    def test_middleware_sets_tenant(self, client, tenant, tenant_user):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/')
        assert response.status_code == 200

    def test_middleware_no_tenant_redirects(self, client, user):
        client.force_login(user)
        response = client.get('/dashboard/')
        assert response.status_code in [302, 403]


class TestTenantUserAPI:
    def test_tenant_users_endpoint(self, tenant_client, tenant):
        client, tenant = tenant_client
        response = client.get(f'/api/tenants/{tenant.pk}/users/')
        assert response.status_code == 200

    def test_tenant_user_list(self, tenant_client, tenant_user):
        client, tenant = tenant_client
        response = client.get('/api/tenants/users/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_tenant_user_create(self, tenant_client, db):
        new_user = User.objects.create_user(
            username='newstaff',
            email='newstaff@test.com',
            password='testpass123'
        )
        client, tenant = tenant_client
        data = {
            'user': new_user.pk,
            'role': 'staff',
        }
        response = client.post('/api/tenants/users/', data)
        assert response.status_code == 201
