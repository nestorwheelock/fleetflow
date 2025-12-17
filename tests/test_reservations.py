import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta, datetime
from decimal import Decimal


class TestReservationModel:
    def test_reservation_creation(self, reservation):
        assert reservation.pk is not None
        assert reservation.status == 'confirmed'

    def test_reservation_str_representation(self, reservation):
        expected = f'Reservation #{reservation.pk} - {reservation.customer} - {reservation.vehicle}'
        assert str(reservation) == expected

    def test_reservation_duration_days(self, reservation):
        assert reservation.duration_days == 2

    def test_reservation_total_calculation(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        reservation = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            daily_rate=Decimal('50.00'),
        )
        assert reservation.total_amount == Decimal('200.00')

    def test_reservation_status_choices(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        valid_statuses = ['pending', 'confirmed', 'checked_out', 'completed', 'cancelled']
        for i, status in enumerate(valid_statuses):
            res = Reservation.objects.create(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=date.today() + timedelta(days=10+i*5),
                end_date=date.today() + timedelta(days=12+i*5),
                status=status,
                daily_rate=Decimal('50.00'),
            )
            assert res.status == status

    def test_reservation_conflict_detection(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        with pytest.raises(ValidationError):
            conflicting = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=date.today() + timedelta(days=3),
                end_date=date.today() + timedelta(days=7),
                status='confirmed',
                daily_rate=Decimal('50.00'),
            )
            conflicting.full_clean()

    def test_reservation_no_conflict_with_cancelled(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=25),
            status='cancelled',
            daily_rate=Decimal('50.00'),
        )
        new_reservation = Reservation(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=22),
            end_date=date.today() + timedelta(days=27),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        new_reservation.full_clean()
        new_reservation.save()
        assert new_reservation.pk is not None

    def test_reservation_start_before_end(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        with pytest.raises(ValidationError):
            res = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=date.today() + timedelta(days=5),
                end_date=date.today() + timedelta(days=2),
                daily_rate=Decimal('50.00'),
            )
            res.full_clean()

    def test_reservation_cannot_start_in_past(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        with pytest.raises(ValidationError):
            res = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=date.today() - timedelta(days=1),
                end_date=date.today() + timedelta(days=2),
                daily_rate=Decimal('50.00'),
            )
            res.full_clean()

    def test_reservation_extras(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        extras = {
            'gps': {'price': 10.00, 'quantity': 1},
            'child_seat': {'price': 15.00, 'quantity': 2},
        }
        reservation = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=33),
            daily_rate=Decimal('50.00'),
            extras=extras,
        )
        assert reservation.extras['gps']['price'] == 10.00

    def test_reservation_notes(self, reservation):
        reservation.notes = 'Customer requested early pickup'
        reservation.save()
        reservation.refresh_from_db()
        assert 'early pickup' in reservation.notes

    def test_reservation_is_active(self, reservation):
        assert reservation.is_active() is True

    def test_reservation_can_checkout(self, reservation):
        assert reservation.can_checkout() is True

    def test_reservation_cannot_checkout_if_cancelled(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        res = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=40),
            end_date=date.today() + timedelta(days=43),
            status='cancelled',
            daily_rate=Decimal('50.00'),
        )
        assert res.can_checkout() is False


class TestReservationConflictPrevention:
    def test_overlapping_start_date(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        base_date = date.today() + timedelta(days=100)
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=base_date,
            end_date=base_date + timedelta(days=4),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        with pytest.raises(ValidationError):
            res = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=base_date + timedelta(days=2),
                end_date=base_date + timedelta(days=7),
                status='confirmed',
                daily_rate=Decimal('50.00'),
            )
            res.full_clean()

    def test_overlapping_end_date(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        base_date = date.today() + timedelta(days=110)
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=base_date + timedelta(days=5),
            end_date=base_date + timedelta(days=10),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        with pytest.raises(ValidationError):
            res = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=base_date + timedelta(days=1),
                end_date=base_date + timedelta(days=7),
                status='confirmed',
                daily_rate=Decimal('50.00'),
            )
            res.full_clean()

    def test_contained_reservation(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        base_date = date.today() + timedelta(days=120)
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=base_date,
            end_date=base_date + timedelta(days=10),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        with pytest.raises(ValidationError):
            res = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=base_date + timedelta(days=3),
                end_date=base_date + timedelta(days=7),
                status='confirmed',
                daily_rate=Decimal('50.00'),
            )
            res.full_clean()

    def test_containing_reservation(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        base_date = date.today() + timedelta(days=130)
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=base_date + timedelta(days=3),
            end_date=base_date + timedelta(days=7),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        with pytest.raises(ValidationError):
            res = Reservation(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=base_date,
                end_date=base_date + timedelta(days=10),
                status='confirmed',
                daily_rate=Decimal('50.00'),
            )
            res.full_clean()

    def test_adjacent_reservations_allowed(self, db, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        base_date = date.today() + timedelta(days=140)
        Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=base_date,
            end_date=base_date + timedelta(days=4),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        res = Reservation(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=base_date + timedelta(days=4),
            end_date=base_date + timedelta(days=9),
            status='confirmed',
            daily_rate=Decimal('50.00'),
        )
        res.full_clean()
        res.save()
        assert res.pk is not None


class TestReservationExtraModel:
    def test_reservation_extra_creation(self, db, tenant):
        from apps.reservations.models import ReservationExtra
        extra = ReservationExtra.objects.create(
            tenant=tenant,
            name='GPS Navigation',
            description='Garmin GPS unit',
            daily_price=Decimal('10.00'),
        )
        assert extra.pk is not None
        assert extra.name == 'GPS Navigation'

    def test_reservation_extra_str_representation(self, db, tenant):
        from apps.reservations.models import ReservationExtra
        extra = ReservationExtra.objects.create(
            tenant=tenant,
            name='Child Seat',
            daily_price=Decimal('15.00'),
        )
        assert str(extra) == 'Child Seat ($15.00/day)'


class TestReservationExtraAPI:
    def test_reservation_extra_list(self, tenant_client, tenant):
        from apps.reservations.models import ReservationExtra
        ReservationExtra.objects.create(
            tenant=tenant,
            name='GPS',
            daily_price=Decimal('10.00'),
        )
        client, tenant = tenant_client
        response = client.get('/api/reservations/extras/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_reservation_extra_create(self, tenant_client):
        client, tenant = tenant_client
        data = {
            'name': 'WiFi Hotspot',
            'description': 'Mobile WiFi device',
            'daily_price': '12.00',
        }
        response = client.post('/api/reservations/extras/', data)
        assert response.status_code == 201


class TestReservationAPI:
    def test_reservation_list_requires_auth(self, api_client):
        response = api_client.get('/api/reservations/')
        assert response.status_code == 403

    def test_reservation_list(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.get('/api/reservations/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_reservation_create(self, tenant_client, vehicle, customer):
        client, tenant = tenant_client
        data = {
            'vehicle': vehicle.pk,
            'customer': customer.pk,
            'start_date': (date.today() + timedelta(days=50)).isoformat(),
            'end_date': (date.today() + timedelta(days=53)).isoformat(),
            'daily_rate': '50.00',
        }
        response = client.post('/api/reservations/', data)
        assert response.status_code == 201

    def test_reservation_create_conflict_rejected(self, tenant_client, reservation, vehicle, customer):
        client, tenant = tenant_client
        data = {
            'vehicle': vehicle.pk,
            'customer': customer.pk,
            'start_date': reservation.start_date.isoformat(),
            'end_date': reservation.end_date.isoformat(),
            'daily_rate': '50.00',
        }
        response = client.post('/api/reservations/', data)
        assert response.status_code == 400

    def test_reservation_update(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.patch(
            f'/api/reservations/{reservation.pk}/',
            {'notes': 'Updated notes'}
        )
        assert response.status_code == 200
        reservation.refresh_from_db()
        assert reservation.notes == 'Updated notes'

    def test_reservation_cancel(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.post(f'/api/reservations/{reservation.pk}/cancel/')
        assert response.status_code == 200
        reservation.refresh_from_db()
        assert reservation.status == 'cancelled'

    def test_reservation_checkout(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.post(f'/api/reservations/{reservation.pk}/checkout/')
        assert response.status_code == 200
        reservation.refresh_from_db()
        assert reservation.status == 'checked_out'

    def test_reservation_checkin(self, tenant_client, reservation):
        client, tenant = tenant_client
        reservation.status = 'checked_out'
        reservation.save()
        response = client.post(f'/api/reservations/{reservation.pk}/checkin/')
        assert response.status_code == 200
        reservation.refresh_from_db()
        assert reservation.status == 'completed'

    def test_reservation_filter_by_status(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.get('/api/reservations/?status=confirmed')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_reservation_filter_by_date_range(self, tenant_client, reservation):
        client, tenant = tenant_client
        start = date.today().isoformat()
        end = (date.today() + timedelta(days=30)).isoformat()
        response = client.get(f'/api/reservations/?start_date_after={start}&start_date_before={end}')
        assert response.status_code == 200

    def test_reservation_calendar_endpoint(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.get('/api/reservations/calendar/')
        assert response.status_code == 200

    def test_check_availability_endpoint(self, tenant_client, vehicle):
        client, tenant = tenant_client
        start = (date.today() + timedelta(days=60)).isoformat()
        end = (date.today() + timedelta(days=65)).isoformat()
        response = client.get(f'/api/reservations/check-availability/?vehicle={vehicle.pk}&start_date={start}&end_date={end}')
        assert response.status_code == 200
        assert response.data['available'] is True

    def test_check_availability_missing_params(self, tenant_client):
        client, tenant = tenant_client
        response = client.get('/api/reservations/check-availability/')
        assert response.status_code == 400

    def test_check_availability_vehicle_not_found(self, tenant_client):
        client, tenant = tenant_client
        start = (date.today() + timedelta(days=60)).isoformat()
        end = (date.today() + timedelta(days=65)).isoformat()
        response = client.get(f'/api/reservations/check-availability/?vehicle=99999&start_date={start}&end_date={end}')
        assert response.status_code == 404

    def test_reservation_today_endpoint(self, tenant_client):
        client, tenant = tenant_client
        response = client.get('/api/reservations/today/')
        assert response.status_code == 200
        assert 'checkouts' in response.data
        assert 'checkins' in response.data

    def test_reservation_upcoming_endpoint(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.get('/api/reservations/upcoming/')
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_reservation_checkout_error_handling(self, tenant_client, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        from decimal import Decimal
        client, _ = tenant_client
        res = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=200),
            end_date=date.today() + timedelta(days=203),
            status='cancelled',
            daily_rate=Decimal('50.00'),
        )
        response = client.post(f'/api/reservations/{res.pk}/checkout/')
        assert response.status_code == 400

    def test_reservation_checkin_error_handling(self, tenant_client, reservation):
        client, tenant = tenant_client
        response = client.post(f'/api/reservations/{reservation.pk}/checkin/')
        assert response.status_code == 400

    def test_reservation_cancel_error_handling(self, tenant_client, tenant, vehicle, customer):
        from apps.reservations.models import Reservation
        from decimal import Decimal
        client, _ = tenant_client
        res = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=210),
            end_date=date.today() + timedelta(days=213),
            status='completed',
            daily_rate=Decimal('50.00'),
        )
        response = client.post(f'/api/reservations/{res.pk}/cancel/')
        assert response.status_code == 400
