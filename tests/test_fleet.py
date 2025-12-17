import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal


class TestVehicleModel:
    def test_vehicle_creation(self, vehicle):
        assert vehicle.pk is not None
        assert vehicle.make == 'Toyota'
        assert vehicle.model == 'Camry'
        assert vehicle.year == 2023

    def test_vehicle_str_representation(self, vehicle):
        expected = '2023 Toyota Camry (ABC123)'
        assert str(vehicle) == expected

    def test_vehicle_default_status(self, db, tenant):
        from apps.fleet.models import Vehicle
        vehicle = Vehicle.objects.create(
            tenant=tenant,
            make='Honda',
            model='Civic',
            year=2023,
            license_plate='XYZ789',
            vin='2HGFC2F59MH123456',
            daily_rate=45.00,
        )
        assert vehicle.status == 'available'

    def test_vehicle_status_choices(self, db, tenant):
        from apps.fleet.models import Vehicle
        valid_statuses = ['available', 'rented', 'maintenance', 'unavailable']
        for i, status in enumerate(valid_statuses):
            vehicle = Vehicle.objects.create(
                tenant=tenant,
                make='Test',
                model=f'Model{status}',
                year=2023,
                license_plate=f'{status[:3].upper()}001',
                vin=f'1HGBH41JXMN{i:06d}',
                status=status,
                daily_rate=50.00,
            )
            assert vehicle.status == status

    def test_vehicle_license_plate_unique_per_tenant(self, db, tenant):
        from apps.fleet.models import Vehicle
        Vehicle.objects.create(
            tenant=tenant,
            make='Toyota',
            model='Corolla',
            year=2023,
            license_plate='UNIQUE01',
            vin='VIN00000000000001',
            daily_rate=50.00,
        )
        with pytest.raises(IntegrityError):
            Vehicle.objects.create(
                tenant=tenant,
                make='Honda',
                model='Accord',
                year=2023,
                license_plate='UNIQUE01',
                vin='VIN00000000000002',
                daily_rate=55.00,
            )

    def test_vehicle_vin_unique(self, db, tenant):
        from apps.fleet.models import Vehicle
        Vehicle.objects.create(
            tenant=tenant,
            make='Toyota',
            model='Corolla',
            year=2023,
            license_plate='VIN001',
            vin='UNIQUEVIN00000001',
            daily_rate=50.00,
        )
        with pytest.raises(IntegrityError):
            Vehicle.objects.create(
                tenant=tenant,
                make='Honda',
                model='Accord',
                year=2023,
                license_plate='VIN002',
                vin='UNIQUEVIN00000001',
                daily_rate=55.00,
            )

    def test_vehicle_daily_rate_positive(self, vehicle):
        assert vehicle.daily_rate > 0

    def test_vehicle_is_available(self, vehicle):
        assert vehicle.is_available() is True

    def test_vehicle_not_available_when_rented(self, db, tenant):
        from apps.fleet.models import Vehicle
        vehicle = Vehicle.objects.create(
            tenant=tenant,
            make='Test',
            model='Rented',
            year=2023,
            license_plate='RENT001',
            vin='RENTEDVIN00000001',
            status='rented',
            daily_rate=50.00,
        )
        assert vehicle.is_available() is False

    def test_vehicle_tenant_isolation(self, db, user, vehicle):
        from apps.tenants.models import Tenant
        from apps.fleet.models import Vehicle
        other_tenant = Tenant.objects.create(
            name='Other Rental',
            slug='other-rental',
            owner=user,
            plan='starter',
            business_name='Other Co',
            business_email='other@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        other_vehicle = Vehicle.objects.create(
            tenant=other_tenant,
            make='Ford',
            model='Mustang',
            year=2023,
            license_plate='OTH001',
            vin='OTHERVIN00000001',
            daily_rate=80.00,
        )
        tenant_vehicles = Vehicle.objects.filter(tenant=vehicle.tenant)
        assert vehicle in tenant_vehicles
        assert other_vehicle not in tenant_vehicles

    def test_vehicle_category(self, db, tenant):
        from apps.fleet.models import Vehicle, VehicleCategory
        category = VehicleCategory.objects.create(
            tenant=tenant,
            name='Economy',
            description='Fuel efficient vehicles'
        )
        vehicle = Vehicle.objects.create(
            tenant=tenant,
            make='Nissan',
            model='Versa',
            year=2023,
            license_plate='ECO001',
            vin='ECONYVIN00000001',
            category=category,
            daily_rate=35.00,
        )
        assert vehicle.category == category


class TestVehicleCategoryModel:
    def test_category_creation(self, db, tenant):
        from apps.fleet.models import VehicleCategory
        category = VehicleCategory.objects.create(
            tenant=tenant,
            name='Luxury',
            description='High-end vehicles'
        )
        assert category.pk is not None
        assert category.name == 'Luxury'

    def test_category_str_representation(self, db, tenant):
        from apps.fleet.models import VehicleCategory
        category = VehicleCategory.objects.create(
            tenant=tenant,
            name='SUV',
            description='Sport utility vehicles'
        )
        assert str(category) == 'SUV'

    def test_category_unique_per_tenant(self, db, tenant):
        from apps.fleet.models import VehicleCategory
        VehicleCategory.objects.create(
            tenant=tenant,
            name='Compact',
            description='Small cars'
        )
        with pytest.raises(IntegrityError):
            VehicleCategory.objects.create(
                tenant=tenant,
                name='Compact',
                description='Another compact'
            )


class TestVehiclePhotoModel:
    def test_photo_creation(self, db, vehicle):
        from apps.fleet.models import VehiclePhoto
        photo = VehiclePhoto.objects.create(
            vehicle=vehicle,
            is_primary=True,
        )
        assert photo.pk is not None
        assert photo.is_primary is True

    def test_only_one_primary_photo(self, db, vehicle):
        from apps.fleet.models import VehiclePhoto
        photo1 = VehiclePhoto.objects.create(
            vehicle=vehicle,
            is_primary=True,
        )
        photo2 = VehiclePhoto.objects.create(
            vehicle=vehicle,
            is_primary=True,
        )
        photo1.refresh_from_db()
        assert photo1.is_primary is False
        assert photo2.is_primary is True


class TestVehicleAPI:
    def test_vehicle_list_requires_auth(self, api_client):
        response = api_client.get('/api/fleet/vehicles/')
        assert response.status_code == 403

    def test_vehicle_list(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.get('/api/fleet/vehicles/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_vehicle_create(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'make': 'Ford',
            'model': 'Focus',
            'year': 2023,
            'license_plate': 'NEW001',
            'vin': 'NEWVIN0000000001',
            'daily_rate': '55.00',
            'status': 'available',
        }
        response = client.post('/api/fleet/vehicles/', data)
        assert response.status_code == 201
        assert response.data['make'] == 'Ford'

    def test_vehicle_update(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.patch(
            f'/api/fleet/vehicles/{vehicle.pk}/',
            {'daily_rate': '60.00'}
        )
        assert response.status_code == 200
        vehicle.refresh_from_db()
        assert vehicle.daily_rate == Decimal('60.00')

    def test_vehicle_delete(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.delete(f'/api/fleet/vehicles/{vehicle.pk}/')
        assert response.status_code == 204

    def test_vehicle_filter_by_status(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.get('/api/fleet/vehicles/?status=available')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_vehicle_search(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.get('/api/fleet/vehicles/?search=Toyota')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_vehicle_available_endpoint(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.get('/api/fleet/vehicles/available/')
        assert response.status_code == 200

    def test_cannot_access_other_tenant_vehicles(self, authenticated_client, vehicle, db, user):
        from apps.tenants.models import Tenant, TenantUser
        other_tenant = Tenant.objects.create(
            name='Other Company',
            slug='other-company',
            owner=user,
            plan='starter',
            business_name='Other',
            business_email='other@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        TenantUser.objects.create(tenant=other_tenant, user=user, role='owner')
        response = authenticated_client.get(f'/api/fleet/vehicles/{vehicle.pk}/')
        assert response.status_code == 404

    def test_vehicle_set_status_endpoint(self, tenant_client, vehicle):
        client, tenant = tenant_client
        data = {'status': 'maintenance'}
        response = client.post(f'/api/fleet/vehicles/{vehicle.pk}/set_status/', data)
        assert response.status_code == 200
        vehicle.refresh_from_db()
        assert vehicle.status == 'maintenance'

    def test_vehicle_set_status_invalid(self, tenant_client, vehicle):
        client, tenant = tenant_client
        data = {'status': 'invalid_status'}
        response = client.post(f'/api/fleet/vehicles/{vehicle.pk}/set_status/', data)
        assert response.status_code == 400


class TestVehicleCategoryAPI:
    def test_category_list(self, tenant_client, tenant):
        from apps.fleet.models import VehicleCategory
        VehicleCategory.objects.create(tenant=tenant, name='SUV')
        client, tenant = tenant_client
        response = client.get('/api/fleet/categories/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_category_create(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'name': 'Luxury',
            'description': 'Premium vehicles',
        }
        response = client.post('/api/fleet/categories/', data)
        assert response.status_code == 201
