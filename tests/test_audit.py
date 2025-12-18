"""Tests for audit logging functionality."""
import pytest
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestActivityLog:
    """Tests for ActivityLog model."""

    def test_create_activity_log(self, tenant, user):
        """Test creating an activity log entry."""
        from apps.tenants.models import ActivityLog

        log = ActivityLog.objects.create(
            tenant=tenant,
            user=user,
            action='create',
            model_name='Vehicle',
            object_id=1,
            object_repr='2024 Toyota Camry',
        )

        assert log.pk is not None
        assert log.tenant == tenant
        assert log.user == user
        assert log.action == 'create'
        assert log.model_name == 'Vehicle'
        assert log.object_id == 1
        assert log.object_repr == '2024 Toyota Camry'
        assert log.timestamp is not None

    def test_activity_log_with_changes(self, tenant, user):
        """Test activity log with change tracking."""
        from apps.tenants.models import ActivityLog

        changes = {
            'status': {'old': 'available', 'new': 'rented'},
            'mileage': {'old': 10000, 'new': 10500},
        }

        log = ActivityLog.objects.create(
            tenant=tenant,
            user=user,
            action='update',
            model_name='Vehicle',
            object_id=1,
            object_repr='2024 Toyota Camry',
            changes=changes,
        )

        assert log.changes == changes
        assert log.changes['status']['old'] == 'available'
        assert log.changes['status']['new'] == 'rented'

    def test_activity_log_str(self, tenant, user):
        """Test activity log string representation."""
        from apps.tenants.models import ActivityLog

        log = ActivityLog.objects.create(
            tenant=tenant,
            user=user,
            action='create',
            model_name='Customer',
            object_id=5,
            object_repr='John Smith',
        )

        assert 'create' in str(log).lower()
        assert 'Customer' in str(log)

    def test_activity_log_actions(self, tenant, user):
        """Test all action types."""
        from apps.tenants.models import ActivityLog

        actions = ['create', 'update', 'delete', 'checkout', 'checkin']

        for action in actions:
            log = ActivityLog.objects.create(
                tenant=tenant,
                user=user,
                action=action,
                model_name='Reservation',
                object_id=1,
                object_repr='Test Reservation',
            )
            assert log.action == action

    def test_activity_log_without_user(self, tenant):
        """Test activity log can be created without user (for system actions)."""
        from apps.tenants.models import ActivityLog

        log = ActivityLog.objects.create(
            tenant=tenant,
            user=None,
            action='update',
            model_name='Vehicle',
            object_id=1,
            object_repr='System Update',
        )

        assert log.user is None
        assert log.pk is not None

    def test_activity_log_ordering(self, tenant, user):
        """Test activity logs are ordered by timestamp descending."""
        from apps.tenants.models import ActivityLog
        import time

        log1 = ActivityLog.objects.create(
            tenant=tenant,
            user=user,
            action='create',
            model_name='Vehicle',
            object_id=1,
            object_repr='First',
        )

        time.sleep(0.1)

        log2 = ActivityLog.objects.create(
            tenant=tenant,
            user=user,
            action='update',
            model_name='Vehicle',
            object_id=1,
            object_repr='Second',
        )

        logs = list(ActivityLog.objects.filter(tenant=tenant))
        assert logs[0] == log2  # Most recent first
        assert logs[1] == log1

    def test_activity_log_filter_by_model(self, tenant, user):
        """Test filtering activity logs by model name."""
        from apps.tenants.models import ActivityLog

        ActivityLog.objects.create(
            tenant=tenant, user=user, action='create',
            model_name='Vehicle', object_id=1, object_repr='Car'
        )
        ActivityLog.objects.create(
            tenant=tenant, user=user, action='create',
            model_name='Customer', object_id=1, object_repr='Person'
        )
        ActivityLog.objects.create(
            tenant=tenant, user=user, action='create',
            model_name='Vehicle', object_id=2, object_repr='Truck'
        )

        vehicle_logs = ActivityLog.objects.filter(tenant=tenant, model_name='Vehicle')
        assert vehicle_logs.count() == 2

        customer_logs = ActivityLog.objects.filter(tenant=tenant, model_name='Customer')
        assert customer_logs.count() == 1


@pytest.mark.django_db
class TestAuditMixin:
    """Tests for AuditMixin functionality on models."""

    def test_vehicle_has_audit_fields(self, tenant):
        """Test that Vehicle model has audit fields."""
        from apps.fleet.models import Vehicle

        vehicle = Vehicle(
            tenant=tenant,
            make='Toyota',
            model='Camry',
            year=2024,
            license_plate='TEST123',
            vin='TEST00000000001',
            status='available',
            daily_rate=50.00,
        )

        # Check audit fields exist
        assert hasattr(vehicle, 'created_by')
        assert hasattr(vehicle, 'updated_by')

    def test_customer_has_audit_fields(self, tenant):
        """Test that Customer model has audit fields."""
        from apps.customers.models import Customer
        from datetime import date

        customer = Customer(
            tenant=tenant,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            license_number='TEST123',
            license_expiry=date(2025, 12, 31),
        )

        assert hasattr(customer, 'created_by')
        assert hasattr(customer, 'updated_by')

    def test_reservation_has_audit_fields(self, tenant, vehicle, customer):
        """Test that Reservation model has audit fields."""
        from apps.reservations.models import Reservation
        from datetime import date
        from decimal import Decimal

        reservation = Reservation(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today(),
            end_date=date.today(),
            status='pending',
            daily_rate=Decimal('50.00'),
            total_amount=Decimal('50.00'),
        )

        assert hasattr(reservation, 'created_by')
        assert hasattr(reservation, 'updated_by')

    def test_audit_fields_can_be_set(self, tenant, user, vehicle, customer):
        """Test that audit fields can be set on save."""
        from apps.reservations.models import Reservation
        from datetime import date
        from decimal import Decimal

        reservation = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today(),
            end_date=date.today(),
            status='pending',
            daily_rate=Decimal('50.00'),
            total_amount=Decimal('50.00'),
            created_by=user,
            updated_by=user,
        )

        assert reservation.created_by == user
        assert reservation.updated_by == user


@pytest.mark.django_db
class TestReservationCheckoutCheckin:
    """Tests for checkout/checkin timestamp and user tracking."""

    def test_reservation_has_checkout_fields(self, reservation):
        """Test that Reservation has checkout tracking fields."""
        assert hasattr(reservation, 'actual_checkout_at')
        assert hasattr(reservation, 'checkout_by')

    def test_reservation_has_checkin_fields(self, reservation):
        """Test that Reservation has checkin tracking fields."""
        assert hasattr(reservation, 'actual_checkin_at')
        assert hasattr(reservation, 'checkin_by')

    def test_checkout_sets_timestamp_and_user(self, reservation, user):
        """Test checkout operation records timestamp and user."""
        from django.utils import timezone

        before = timezone.now()
        reservation.actual_checkout_at = timezone.now()
        reservation.checkout_by = user
        reservation.status = 'checked_out'
        reservation.save()

        reservation.refresh_from_db()
        assert reservation.actual_checkout_at is not None
        assert reservation.actual_checkout_at >= before
        assert reservation.checkout_by == user

    def test_checkin_sets_timestamp_and_user(self, reservation, user):
        """Test checkin operation records timestamp and user."""
        from django.utils import timezone

        # First checkout
        reservation.actual_checkout_at = timezone.now()
        reservation.checkout_by = user
        reservation.status = 'checked_out'
        reservation.save()

        # Then checkin
        before = timezone.now()
        reservation.actual_checkin_at = timezone.now()
        reservation.checkin_by = user
        reservation.status = 'completed'
        reservation.save()

        reservation.refresh_from_db()
        assert reservation.actual_checkin_at is not None
        assert reservation.actual_checkin_at >= before
        assert reservation.checkin_by == user


@pytest.mark.django_db
class TestActivityLogHelper:
    """Tests for activity logging helper function."""

    def test_log_activity_creates_entry(self, tenant, user, vehicle):
        """Test the log_activity helper function."""
        from apps.tenants.models import ActivityLog, log_activity

        log_activity(
            tenant=tenant,
            user=user,
            action='create',
            instance=vehicle,
        )

        log = ActivityLog.objects.filter(
            tenant=tenant,
            model_name='Vehicle',
            object_id=vehicle.pk,
        ).first()

        assert log is not None
        assert log.action == 'create'
        assert log.user == user

    def test_log_activity_with_changes(self, tenant, user, vehicle):
        """Test logging activity with field changes."""
        from apps.tenants.models import ActivityLog, log_activity

        changes = {'status': {'old': 'available', 'new': 'maintenance'}}

        log_activity(
            tenant=tenant,
            user=user,
            action='update',
            instance=vehicle,
            changes=changes,
        )

        log = ActivityLog.objects.filter(
            tenant=tenant,
            model_name='Vehicle',
            object_id=vehicle.pk,
            action='update',
        ).first()

        assert log is not None
        assert log.changes == changes


@pytest.mark.django_db
class TestPhotoUploadAuditLogging:
    """Tests for B-005: Photo upload audit logging.

    These tests verify that photo uploads are properly logged
    in the ActivityLog for audit purposes.
    """

    def test_vehicle_photo_upload_creates_activity_log(self, tenant, user, vehicle):
        """Test that uploading a vehicle photo creates an activity log entry.

        B-005: This test should FAIL until the bug is fixed.
        Photo uploads should be logged with action 'upload'.
        """
        from apps.tenants.models import ActivityLog
        from apps.fleet.models import VehiclePhoto
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        from apps.dashboard.views import vehicle_photo_upload
        from io import BytesIO
        from PIL import Image

        # Create request factory
        factory = RequestFactory()

        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        test_image = SimpleUploadedFile(
            name='test_photo.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )

        # Create POST request
        request = factory.post(
            f'/dashboard/vehicles/{vehicle.pk}/photos/upload/',
        )
        request.FILES.setlist('photos', [test_image])
        request.user = user
        request.tenant = tenant

        # Call the view directly
        response = vehicle_photo_upload(request, vehicle.pk)

        # Check the upload succeeded
        assert response.status_code == 200

        # Verify photo was created
        assert VehiclePhoto.objects.filter(vehicle=vehicle).exists()

        # B-005: Check that an activity log was created for this upload
        # This assertion should FAIL until the bug is fixed
        log = ActivityLog.objects.filter(
            tenant=tenant,
            model_name='VehiclePhoto',
            action='upload',
        ).first()

        assert log is not None, "Photo upload should create an ActivityLog entry"
        assert log.user == user
        assert log.action == 'upload'

    def test_vehicle_photo_delete_creates_activity_log(self, tenant, user, vehicle):
        """Test that deleting a vehicle photo creates an activity log entry.

        B-005: This test should FAIL until the bug is fixed.
        """
        from apps.tenants.models import ActivityLog
        from apps.fleet.models import VehiclePhoto
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        from apps.dashboard.views import vehicle_photo_delete
        from io import BytesIO
        from PIL import Image

        factory = RequestFactory()

        # Create a photo to delete
        image = Image.new('RGB', (100, 100), color='blue')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        photo = VehiclePhoto.objects.create(
            vehicle=vehicle,
            image=SimpleUploadedFile(
                name='test_delete.jpg',
                content=image_io.read(),
                content_type='image/jpeg'
            ),
        )
        photo_pk = photo.pk

        # Create POST request for delete
        request = factory.post(
            f'/dashboard/vehicles/{vehicle.pk}/photos/{photo_pk}/delete/',
        )
        request.user = user
        request.tenant = tenant

        # Call the view directly
        response = vehicle_photo_delete(request, vehicle.pk, photo_pk)

        assert response.status_code == 200

        # Verify photo was deleted
        assert not VehiclePhoto.objects.filter(pk=photo_pk).exists()

        # B-005: Check that an activity log was created for this delete
        log = ActivityLog.objects.filter(
            tenant=tenant,
            model_name='VehiclePhoto',
            action='delete',
        ).first()

        assert log is not None, "Photo delete should create an ActivityLog entry"
        assert log.user == user
        assert log.action == 'delete'
