"""
Tests for missing CRUD operations - B-003
Tests for FullCalendar integration - B-002
"""
import pytest
from datetime import date, timedelta
from django.urls import reverse


class TestCalendarView:
    """Tests for FullCalendar integration - B-002"""

    def test_calendar_page_accessible(self, client, tenant_user):
        """Calendar page should be accessible"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/calendar/')
        assert response.status_code == 200

    def test_calendar_page_has_fullcalendar_script(self, client, tenant_user):
        """Calendar page should include FullCalendar library script"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/calendar/')
        # Check for FullCalendar CDN script tag
        assert b'cdn.jsdelivr.net/npm/fullcalendar' in response.content or b'fullcalendar' in response.content.lower()
        # Check for calendar initialization
        assert b'FullCalendar.Calendar' in response.content or b'new Calendar' in response.content

    def test_calendar_page_has_calendar_div(self, client, tenant_user):
        """Calendar page should have calendar container"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/reservations/calendar/')
        assert b'id="calendar"' in response.content

    def test_calendar_api_returns_events(self, tenant_client, reservation):
        """Calendar API should return reservation events"""
        client, tenant = tenant_client
        response = client.get('/api/reservations/calendar/')
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_calendar_api_event_format(self, tenant_client, reservation):
        """Calendar API should return FullCalendar compatible format"""
        client, tenant = tenant_client
        response = client.get('/api/reservations/calendar/')
        assert response.status_code == 200
        if len(response.data) > 0:
            event = response.data[0]
            assert 'id' in event
            assert 'title' in event
            assert 'start' in event
            assert 'end' in event
            assert 'color' in event

    def test_calendar_end_date_is_exclusive(self, tenant_client, reservation):
        """B-007: Calendar end date should be exclusive (one day after actual end).

        FullCalendar treats end dates as exclusive for all-day events.
        If a reservation is Dec 18-20, we need to return end as Dec 21.
        """
        client, tenant = tenant_client
        response = client.get('/api/reservations/calendar/')
        assert response.status_code == 200
        if len(response.data) > 0:
            event = response.data[0]
            # Find the matching reservation
            from apps.reservations.models import Reservation
            res = Reservation.objects.get(pk=event['id'])
            # End date in API should be one day after actual end_date
            expected_end = res.end_date + timedelta(days=1)
            # Compare as dates (response may be date object or string)
            event_end = event['end']
            if isinstance(event_end, str):
                event_end = date.fromisoformat(event_end)
            assert event_end == expected_end, f"Expected {expected_end}, got {event_end}"


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


class TestCustomerLicenseUpload:
    """Tests for customer driver's license image upload"""

    def test_customer_form_has_license_upload_fields(self, client, tenant_user):
        """Customer form should have file upload fields for license images"""
        client.force_login(tenant_user.user)
        response = client.get('/dashboard/customers/create/')
        assert b'license_image_front' in response.content
        assert b'license_image_back' in response.content
        assert b'enctype="multipart/form-data"' in response.content

    def test_customer_form_accepts_license_images(self, client, tenant_user):
        """Customer create should accept license image uploads"""
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        client.force_login(tenant_user.user)

        # Create test images
        def create_test_image(name):
            img = Image.new('RGB', (100, 100), color='red')
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            return SimpleUploadedFile(name, buffer.read(), content_type='image/jpeg')

        front_image = create_test_image('license_front.jpg')
        back_image = create_test_image('license_back.jpg')

        data = {
            'first_name': 'License',
            'last_name': 'Test',
            'email': 'license.test@example.com',
            'phone': '555-9999',
            'license_image_front': front_image,
            'license_image_back': back_image,
        }
        response = client.post('/dashboard/customers/create/', data)
        assert response.status_code == 302  # Redirect on success

        from apps.customers.models import Customer
        customer = Customer.objects.get(email='license.test@example.com')
        assert customer.license_image_front
        assert customer.license_image_back

    def test_customer_detail_shows_license_images(self, client, tenant_user, customer):
        """Customer detail page should show license images if uploaded"""
        from io import BytesIO
        from PIL import Image
        from django.core.files.base import ContentFile

        client.force_login(tenant_user.user)

        # Add test images to customer
        img = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        customer.license_image_front.save('front.jpg', ContentFile(buffer.getvalue()))

        buffer.seek(0)
        customer.license_image_back.save('back.jpg', ContentFile(buffer.getvalue()))
        customer.save()

        response = client.get(f'/dashboard/customers/{customer.pk}/')
        assert response.status_code == 200
        # Check for license images section or view link
        assert b'license' in response.content.lower()

    def test_combined_license_view_accessible(self, client, tenant_user, customer):
        """Combined license view should be accessible for customers with images"""
        from io import BytesIO
        from PIL import Image
        from django.core.files.base import ContentFile

        client.force_login(tenant_user.user)

        # Add test images to customer
        img = Image.new('RGB', (100, 100), color='green')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        customer.license_image_front.save('front.jpg', ContentFile(buffer.getvalue()))

        buffer.seek(0)
        customer.license_image_back.save('back.jpg', ContentFile(buffer.getvalue()))
        customer.save()

        response = client.get(f'/dashboard/customers/{customer.pk}/license/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'image/jpeg'

    def test_combined_license_returns_404_without_images(self, client, tenant_user, customer):
        """Combined license view should return 404 if no images uploaded"""
        client.force_login(tenant_user.user)
        response = client.get(f'/dashboard/customers/{customer.pk}/license/')
        assert response.status_code == 404
