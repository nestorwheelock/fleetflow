import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta


class TestCustomerModel:
    def test_customer_creation(self, customer):
        assert customer.pk is not None
        assert customer.first_name == 'John'
        assert customer.last_name == 'Doe'
        assert customer.email == 'john.doe@example.com'

    def test_customer_str_representation(self, customer):
        assert str(customer) == 'John Doe'

    def test_customer_full_name(self, customer):
        assert customer.full_name == 'John Doe'

    def test_customer_email_unique_per_tenant(self, db, tenant):
        from apps.customers.models import Customer
        Customer.objects.create(
            tenant=tenant,
            first_name='Jane',
            last_name='Smith',
            email='unique@test.com',
            phone='555-0001',
        )
        with pytest.raises(IntegrityError):
            Customer.objects.create(
                tenant=tenant,
                first_name='Bob',
                last_name='Jones',
                email='unique@test.com',
                phone='555-0002',
            )

    def test_customer_license_expiry_validation(self, db, tenant):
        from apps.customers.models import Customer
        customer = Customer.objects.create(
            tenant=tenant,
            first_name='Test',
            last_name='User',
            email='testlicense@test.com',
            phone='555-0003',
            license_number='TEST12345',
            license_expiry=date.today() - timedelta(days=1),
        )
        assert customer.is_license_expired() is True

    def test_customer_license_valid(self, customer):
        assert customer.is_license_expired() is False

    def test_customer_age_calculation(self, customer):
        from datetime import date
        expected_age = (date.today() - date(1985, 5, 15)).days // 365
        assert customer.age == expected_age

    def test_customer_minimum_age(self, db, tenant):
        from apps.customers.models import Customer
        customer = Customer(
            tenant=tenant,
            first_name='Young',
            last_name='Driver',
            email='young@test.com',
            phone='555-0004',
            date_of_birth=date.today() - timedelta(days=365*17),
        )
        assert customer.is_eligible_to_rent() is False

    def test_customer_eligible_to_rent(self, customer):
        assert customer.is_eligible_to_rent() is True

    def test_customer_blacklist(self, db, tenant):
        from apps.customers.models import Customer
        customer = Customer.objects.create(
            tenant=tenant,
            first_name='Banned',
            last_name='Customer',
            email='banned@test.com',
            phone='555-0005',
            is_blacklisted=True,
            blacklist_reason='Multiple accidents',
        )
        assert customer.is_blacklisted is True
        assert customer.is_eligible_to_rent() is False

    def test_customer_rental_history(self, customer, reservation):
        history = customer.get_rental_history()
        assert reservation in history

    def test_customer_total_rentals(self, customer, reservation):
        assert customer.total_rentals == 1

    def test_customer_notes(self, db, tenant):
        from apps.customers.models import Customer
        customer = Customer.objects.create(
            tenant=tenant,
            first_name='Note',
            last_name='Taker',
            email='notes@test.com',
            phone='555-0006',
            notes='VIP customer, provide free upgrade when available',
        )
        assert 'VIP' in customer.notes

    def test_customer_tenant_isolation(self, db, customer, user):
        from apps.tenants.models import Tenant
        from apps.customers.models import Customer
        other_tenant = Tenant.objects.create(
            name='Other Rental',
            slug='other-rental-cust',
            owner=user,
            plan='starter',
            business_name='Other Co',
            business_email='other@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        other_customer = Customer.objects.create(
            tenant=other_tenant,
            first_name='Other',
            last_name='Customer',
            email='other@customer.com',
            phone='555-0007',
        )
        tenant_customers = Customer.objects.filter(tenant=customer.tenant)
        assert customer in tenant_customers
        assert other_customer not in tenant_customers


class TestCustomerAPI:
    def test_customer_list_requires_auth(self, api_client):
        response = api_client.get('/api/customers/')
        assert response.status_code == 403

    def test_customer_list(self, tenant_client, customer):
        client, tenant = tenant_client
        response = client.get('/api/customers/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_customer_create(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'new.customer@test.com',
            'phone': '555-9999',
        }
        response = client.post('/api/customers/', data)
        assert response.status_code == 201
        assert response.data['first_name'] == 'New'

    def test_customer_create_with_license(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'first_name': 'Licensed',
            'last_name': 'Driver',
            'email': 'licensed@test.com',
            'phone': '555-8888',
            'license_number': 'DL99999999',
            'license_state': 'CA',
            'license_expiry': '2026-12-31',
            'date_of_birth': '1990-01-15',
        }
        response = client.post('/api/customers/', data)
        assert response.status_code == 201
        assert response.data['license_number'] == 'DL99999999'

    def test_customer_update(self, tenant_client, customer):
        client, tenant = tenant_client
        response = client.patch(
            f'/api/customers/{customer.pk}/',
            {'phone': '555-0000'}
        )
        assert response.status_code == 200
        customer.refresh_from_db()
        assert customer.phone == '555-0000'

    def test_customer_delete(self, tenant_client, customer):
        client, tenant = tenant_client
        response = client.delete(f'/api/customers/{customer.pk}/')
        assert response.status_code == 204

    def test_customer_search_by_name(self, tenant_client, customer):
        client, tenant = tenant_client
        response = client.get('/api/customers/?search=John')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_customer_search_by_email(self, tenant_client, customer):
        client, tenant = tenant_client
        response = client.get('/api/customers/?search=john.doe')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_customer_filter_blacklisted(self, tenant_client, db, tenant):
        from apps.customers.models import Customer
        client, _ = tenant_client
        Customer.objects.create(
            tenant=tenant,
            first_name='Bad',
            last_name='Actor',
            email='bad@test.com',
            phone='555-0008',
            is_blacklisted=True,
        )
        response = client.get('/api/customers/?is_blacklisted=true')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['first_name'] == 'Bad'

    def test_customer_rental_history_endpoint(self, tenant_client, customer, reservation):
        client, tenant = tenant_client
        response = client.get(f'/api/customers/{customer.pk}/rentals/')
        assert response.status_code == 200

    def test_cannot_access_other_tenant_customers(self, authenticated_client, customer, db, user):
        from apps.tenants.models import Tenant, TenantUser
        other_tenant = Tenant.objects.create(
            name='Other Company',
            slug='other-company-cust',
            owner=user,
            plan='starter',
            business_name='Other',
            business_email='other@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        TenantUser.objects.create(tenant=other_tenant, user=user, role='owner')
        response = authenticated_client.get(f'/api/customers/{customer.pk}/')
        assert response.status_code == 404

    def test_customer_blacklist_endpoint(self, tenant_client, customer):
        client, tenant = tenant_client
        data = {'reason': 'Damaged vehicle'}
        response = client.post(f'/api/customers/{customer.pk}/blacklist/', data)
        assert response.status_code == 200
        customer.refresh_from_db()
        assert customer.is_blacklisted is True
        assert customer.blacklist_reason == 'Damaged vehicle'

    def test_customer_unblacklist_endpoint(self, tenant_client, customer):
        client, tenant = tenant_client
        customer.is_blacklisted = True
        customer.blacklist_reason = 'Test'
        customer.save()
        response = client.post(f'/api/customers/{customer.pk}/unblacklist/')
        assert response.status_code == 200
        customer.refresh_from_db()
        assert customer.is_blacklisted is False
        assert customer.blacklist_reason == ''
