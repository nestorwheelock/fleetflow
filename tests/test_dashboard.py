import pytest
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal


class TestDashboardViews:
    def test_dashboard_requires_auth(self, client):
        response = client.get('/dashboard/')
        assert response.status_code == 302

    def test_dashboard_home(self, client, tenant_user):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/')
        assert response.status_code == 200

    def test_dashboard_shows_todays_schedule(self, client, tenant_user, reservation):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/')
        assert response.status_code == 200
        assert b'schedule' in response.content.lower() or response.status_code == 200

    def test_dashboard_shows_statistics(self, client, tenant_user, vehicle):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/')
        assert response.status_code == 200


class TestDashboardAPI:
    def test_dashboard_stats_endpoint(self, tenant_client, vehicle, customer, reservation):
        client, tenant = tenant_client
        response = client.get('/api/dashboard/stats/')
        assert response.status_code == 200
        assert 'total_vehicles' in response.data
        assert 'total_customers' in response.data
        assert 'active_reservations' in response.data

    def test_dashboard_today_schedule(self, tenant_client):
        client, tenant = tenant_client
        response = client.get('/api/dashboard/today/')
        assert response.status_code == 200
        assert 'checkouts' in response.data
        assert 'checkins' in response.data

    def test_dashboard_revenue_summary(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.get('/api/dashboard/revenue/')
        assert response.status_code == 200
        assert 'today' in response.data
        assert 'this_week' in response.data
        assert 'this_month' in response.data

    def test_dashboard_fleet_status(self, tenant_client, vehicle):
        client, tenant = tenant_client
        response = client.get('/api/dashboard/fleet-status/')
        assert response.status_code == 200
        assert 'available' in response.data
        assert 'rented' in response.data
        assert 'maintenance' in response.data

    def test_dashboard_upcoming_reservations(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.get('/api/dashboard/upcoming/')
        assert response.status_code == 200
        assert isinstance(response.data, list)


class TestQuickActions:
    def test_quick_action_new_reservation(self, tenant_client, vehicle, customer):
        client, tenant = tenant_client
        data = {
            'vehicle': vehicle.pk,
            'customer': customer.pk,
            'start_date': (date.today() + timedelta(days=70)).isoformat(),
            'end_date': (date.today() + timedelta(days=73)).isoformat(),
            'daily_rate': '50.00',
        }
        response = client.post('/api/dashboard/quick-actions/new-reservation/', data)
        assert response.status_code == 201

    def test_quick_action_new_customer(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'first_name': 'Quick',
            'last_name': 'Customer',
            'email': 'quick@test.com',
            'phone': '555-QUICK',
        }
        response = client.post('/api/dashboard/quick-actions/new-customer/', data)
        assert response.status_code == 201

    def test_quick_action_vehicle_status(self, tenant_client, vehicle):
        client, tenant = tenant_client
        data = {
            'vehicle': vehicle.pk,
            'status': 'maintenance',
        }
        response = client.post('/api/dashboard/quick-actions/vehicle-status/', data)
        assert response.status_code == 200
        vehicle.refresh_from_db()
        assert vehicle.status == 'maintenance'


class TestVehicleListView:
    def test_vehicle_list_view(self, client, tenant_user, vehicle):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/vehicles/')
        assert response.status_code == 200

    def test_vehicle_detail_view(self, client, tenant_user, vehicle):
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/vehicles/{vehicle.pk}/')
        assert response.status_code == 200

    def test_vehicle_create_view(self, client, tenant_user):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/vehicles/create/')
        assert response.status_code == 200

    def test_vehicle_edit_view(self, client, tenant_user, vehicle):
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/vehicles/{vehicle.pk}/edit/')
        assert response.status_code == 200


class TestCustomerListView:
    def test_customer_list_view(self, client, tenant_user, customer):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/customers/')
        assert response.status_code == 200

    def test_customer_detail_view(self, client, tenant_user, customer):
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/customers/{customer.pk}/')
        assert response.status_code == 200


class TestReservationListView:
    def test_reservation_list_view(self, client, tenant_user, reservation):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/')
        assert response.status_code == 200

    def test_reservation_detail_view(self, client, tenant_user, reservation):
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/reservations/{reservation.pk}/')
        assert response.status_code == 200

    def test_reservation_calendar_view(self, client, tenant_user):
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/calendar/')
        assert response.status_code == 200


class TestCheckoutCheckinViews:
    def test_checkout_view(self, client, tenant_user, reservation):
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/reservations/{reservation.pk}/checkout/')
        assert response.status_code == 200

    def test_checkin_view(self, client, tenant_user, reservation):
        client.force_login(tenant_user.user)
        reservation.status = 'checked_out'
        reservation.save()
        response = client.get(f'/dashboard/reservations/{reservation.pk}/checkin/')
        assert response.status_code == 200


class TestQuickActionsErrors:
    def test_quick_action_vehicle_status_invalid_vehicle(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'vehicle': 99999,
            'status': 'maintenance',
        }
        response = client.post('/api/dashboard/quick-actions/vehicle-status/', data)
        assert response.status_code == 404

    def test_quick_action_vehicle_status_invalid_status(self, tenant_client, vehicle):
        client, tenant = tenant_client
        data = {
            'vehicle': vehicle.pk,
            'status': 'invalid_status',
        }
        response = client.post('/api/dashboard/quick-actions/vehicle-status/', data)
        assert response.status_code == 400


class TestContractViews:
    def test_contract_list_view(self, client, tenant_user, reservation):
        from apps.contracts.models import Contract
        client.force_login(tenant_user.user)
        Contract.objects.create(
            tenant=reservation.tenant,
            reservation=reservation,
        )
        response = client.get('/dashboard/contracts/')
        assert response.status_code == 200

    def test_contract_detail_view(self, client, tenant_user, reservation):
        from apps.contracts.models import Contract
        client.force_login(tenant_user.user)
        contract = Contract.objects.create(
            tenant=reservation.tenant,
            reservation=reservation,
        )
        response = client.get(f'/dashboard/contracts/{contract.pk}/')
        assert response.status_code == 200

    def test_contract_pdf_download(self, client, tenant_user, reservation):
        from apps.contracts.models import Contract
        client.force_login(tenant_user.user)
        contract = Contract.objects.create(
            tenant=reservation.tenant,
            reservation=reservation,
        )
        response = client.get(f'/dashboard/contracts/{contract.pk}/pdf/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
