"""
Tests for missing CRUD operations - B-003
"""
import pytest
from datetime import date, timedelta
from django.urls import reverse


class TestCustomerCRUD:
    """Tests for Customer create/edit/delete views"""

    def test_customer_create_view_accessible(self, client, tenant_user):
        """Customer create page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/customers/create/')
        assert response.status_code == 200

    def test_customer_create_view_has_form(self, client, tenant_user):
        """Customer create page should have a form"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/customers/create/')
        assert b'<form' in response.content
        assert b'first_name' in response.content.lower()
        assert b'last_name' in response.content.lower()
        assert b'email' in response.content.lower()

    def test_customer_create_post_creates_customer(self, client, tenant_user):
        """POST to customer create should create a customer"""
        client.force_login(tenant_user.user)
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Austin',
            'state': 'TX',
            'zip_code': '78701',
        }
        response = client.post('/dashboard/customers/create/', data)
        assert response.status_code == 302  # Redirect on success

    def test_customer_edit_view_accessible(self, client, tenant_user, customer):
        """Customer edit page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/customers/{customer.pk}/edit/')
        assert response.status_code == 200

    def test_customer_edit_view_has_form_with_data(self, client, tenant_user, customer):
        """Customer edit page should have form pre-filled with data"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/customers/{customer.pk}/edit/')
        assert response.status_code == 200
        assert customer.first_name.encode() in response.content

    def test_customer_edit_post_updates_customer(self, client, tenant_user, customer):
        """POST to customer edit should update the customer"""
        client.force_login(tenant_user.user)
        data = {
            'first_name': 'Updated',
            'last_name': customer.last_name,
            'email': customer.email,
            'phone': customer.phone or '555-0000',
        }
        response = client.post(f'/dashboard/customers/{customer.pk}/edit/', data)
        assert response.status_code == 302
        customer.refresh_from_db()
        assert customer.first_name == 'Updated'

    def test_customer_delete_view_accessible(self, client, tenant_user, customer):
        """Customer delete confirmation page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/customers/{customer.pk}/delete/')
        assert response.status_code == 200

    def test_customer_delete_post_deletes_customer(self, client, tenant_user, customer):
        """POST to customer delete should delete the customer"""
        from apps.customers.models import Customer
        client.force_login(tenant_user.user)
        pk = customer.pk
        response = client.post(f'/dashboard/customers/{pk}/delete/')
        assert response.status_code == 302
        assert not Customer.objects.filter(pk=pk).exists()


class TestReservationCRUD:
    """Tests for Reservation create/edit/cancel views"""

    def test_reservation_create_view_accessible(self, client, tenant_user):
        """Reservation create page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/create/')
        assert response.status_code == 200

    def test_reservation_create_view_has_form(self, client, tenant_user):
        """Reservation create page should have a form"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/create/')
        assert b'<form' in response.content
        assert b'vehicle' in response.content.lower()
        assert b'customer' in response.content.lower()

    def test_reservation_create_post_creates_reservation(self, client, tenant_user, vehicle, customer):
        """POST to reservation create should create a reservation"""
        client.force_login(tenant_user.user)
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        data = {
            'vehicle': vehicle.pk,
            'customer': customer.pk,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily_rate': '50.00',
        }
        response = client.post('/dashboard/reservations/create/', data)
        assert response.status_code == 302  # Redirect on success

    def test_reservation_edit_view_accessible(self, client, tenant_user, reservation):
        """Reservation edit page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/reservations/{reservation.pk}/edit/')
        assert response.status_code == 200

    def test_reservation_edit_post_updates_reservation(self, client, tenant_user, reservation):
        """POST to reservation edit should update the reservation"""
        client.force_login(tenant_user.user)
        new_rate = '75.00'
        data = {
            'vehicle': reservation.vehicle.pk,
            'customer': reservation.customer.pk,
            'start_date': reservation.start_date.isoformat(),
            'end_date': reservation.end_date.isoformat(),
            'daily_rate': new_rate,
        }
        response = client.post(f'/dashboard/reservations/{reservation.pk}/edit/', data)
        assert response.status_code == 302
        reservation.refresh_from_db()
        assert str(reservation.daily_rate) == new_rate

    def test_reservation_cancel_view_accessible(self, client, tenant_user, reservation):
        """Reservation cancel confirmation page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/reservations/{reservation.pk}/cancel/')
        assert response.status_code == 200

    def test_reservation_cancel_post_cancels_reservation(self, client, tenant_user, reservation):
        """POST to reservation cancel should cancel the reservation"""
        client.force_login(tenant_user.user)
        response = client.post(f'/dashboard/reservations/{reservation.pk}/cancel/')
        assert response.status_code == 302
        reservation.refresh_from_db()
        assert reservation.status == 'cancelled'


class TestVehicleDelete:
    """Tests for Vehicle delete view"""

    def test_vehicle_delete_view_accessible(self, client, tenant_user, vehicle):
        """Vehicle delete confirmation page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/vehicles/{vehicle.pk}/delete/')
        assert response.status_code == 200

    def test_vehicle_delete_post_deletes_vehicle(self, client, tenant_user, vehicle):
        """POST to vehicle delete should delete the vehicle"""
        from apps.fleet.models import Vehicle
        client.force_login(tenant_user.user)
        pk = vehicle.pk
        response = client.post(f'/dashboard/vehicles/{pk}/delete/')
        assert response.status_code == 302
        assert not Vehicle.objects.filter(pk=pk).exists()

    def test_vehicle_delete_button_on_detail_page(self, client, tenant_user, vehicle):
        """Vehicle detail page should have delete button"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/vehicles/{vehicle.pk}/')
        assert b'delete' in response.content.lower()
