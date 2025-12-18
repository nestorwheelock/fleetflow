from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.tenants.utils import get_tenant_from_request
from .models import Reservation, ReservationExtra


class ReservationExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationExtra
        fields = ['id', 'name', 'description', 'daily_price', 'is_active']
        read_only_fields = ['id']


class ReservationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()
    duration_days = serializers.IntegerField(read_only=True)
    can_checkout = serializers.SerializerMethodField()
    can_checkin = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'vehicle', 'vehicle_name', 'customer', 'customer_name',
            'start_date', 'end_date', 'pickup_time', 'return_time',
            'status', 'daily_rate', 'total_amount', 'deposit_amount',
            'discount_amount', 'tax_amount', 'extras', 'notes',
            'duration_days', 'actual_checkout_at', 'actual_checkin_at',
            'checkout_mileage', 'checkin_mileage',
            'can_checkout', 'can_checkin', 'can_cancel',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'total_amount', 'actual_checkout_at', 'actual_checkin_at',
            'created_at', 'updated_at',
        ]

    def get_vehicle_name(self, obj):
        return str(obj.vehicle)

    def get_can_checkout(self, obj):
        return obj.can_checkout()

    def get_can_checkin(self, obj):
        return obj.can_checkin()

    def get_can_cancel(self, obj):
        return obj.can_cancel()

    def validate(self, data):
        vehicle = data.get('vehicle') or (self.instance.vehicle if self.instance else None)
        start_date = data.get('start_date') or (self.instance.start_date if self.instance else None)
        end_date = data.get('end_date') or (self.instance.end_date if self.instance else None)

        if vehicle and start_date and end_date:
            exclude_pk = self.instance.pk if self.instance else None
            if not Reservation.check_availability(vehicle, start_date, end_date, exclude_pk):
                raise serializers.ValidationError(
                    'This vehicle is already reserved for the selected dates.'
                )

        return data

    def create(self, validated_data):
        tenant = get_tenant_from_request(self.context['request'])
        if not tenant:
            raise serializers.ValidationError('No tenant associated with request')
        validated_data['tenant'] = tenant
        instance = Reservation(**validated_data)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))
        instance.save()
        return instance


class ReservationListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'vehicle', 'vehicle_name', 'customer', 'customer_name',
            'start_date', 'end_date', 'status', 'total_amount',
        ]

    def get_vehicle_name(self, obj):
        return str(obj.vehicle)


class CalendarEventSerializer(serializers.ModelSerializer):
    """Serializer for FullCalendar events.

    Note: FullCalendar treats the 'end' date as EXCLUSIVE for all-day events.
    If a reservation is from Dec 18 to Dec 20, we need to return end as Dec 21.
    """
    title = serializers.SerializerMethodField()
    start = serializers.DateField(source='start_date')
    end = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'start', 'end', 'color', 'status']

    def get_title(self, obj):
        return f'{obj.vehicle} - {obj.customer}'

    def get_end(self, obj):
        """Return end date + 1 day for FullCalendar's exclusive end date handling."""
        from datetime import timedelta
        return obj.end_date + timedelta(days=1)

    def get_color(self, obj):
        colors = {
            'pending': '#fbbf24',
            'confirmed': '#3b82f6',
            'checked_out': '#10b981',
            'completed': '#6b7280',
            'cancelled': '#ef4444',
            'no_show': '#f97316',
        }
        return colors.get(obj.status, '#6b7280')


class AvailabilityCheckSerializer(serializers.Serializer):
    vehicle = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    available = serializers.BooleanField(read_only=True)
