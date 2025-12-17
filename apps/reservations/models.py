from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date

from apps.tenants.models import TenantModel
from apps.fleet.models import Vehicle
from apps.customers.models import Customer


class Reservation(TenantModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_out', 'Checked Out'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='reservations'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='reservations'
    )

    start_date = models.DateField()
    end_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    return_time = models.TimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    extras = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    actual_checkout_at = models.DateTimeField(null=True, blank=True)
    actual_checkin_at = models.DateTimeField(null=True, blank=True)
    checkout_mileage = models.PositiveIntegerField(null=True, blank=True)
    checkin_mileage = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']

    def __str__(self):
        return f'Reservation #{self.pk} - {self.customer} - {self.vehicle}'

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    def clean(self):
        super().clean()

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date.'
                })

            if not self.pk and self.start_date < date.today():
                raise ValidationError({
                    'start_date': 'Start date cannot be in the past.'
                })

        if self.vehicle_id and self.start_date and self.end_date:
            if self.status not in ['cancelled', 'no_show']:
                if self.has_conflict():
                    raise ValidationError(
                        'This vehicle is already reserved for the selected dates.'
                    )

    def has_conflict(self):
        conflicting = Reservation.objects.filter(
            vehicle=self.vehicle,
            status__in=['pending', 'confirmed', 'checked_out'],
        ).exclude(pk=self.pk)

        conflicting = conflicting.filter(
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        )

        return conflicting.exists()

    def save(self, *args, **kwargs):
        if not self.total_amount or self.total_amount == Decimal('0.00'):
            self.calculate_total()
        super().save(*args, **kwargs)

    def calculate_total(self):
        base_amount = self.daily_rate * self.duration_days

        extras_total = Decimal('0.00')
        if self.extras:
            for extra in self.extras.values():
                if isinstance(extra, dict):
                    price = Decimal(str(extra.get('price', 0)))
                    quantity = extra.get('quantity', 1)
                    extras_total += price * quantity * self.duration_days

        subtotal = base_amount + extras_total - self.discount_amount
        self.total_amount = subtotal + self.tax_amount

    def is_active(self):
        return self.status in ['pending', 'confirmed', 'checked_out']

    def can_checkout(self):
        return self.status in ['pending', 'confirmed']

    def can_checkin(self):
        return self.status == 'checked_out'

    def can_cancel(self):
        return self.status in ['pending', 'confirmed']

    def checkout(self, mileage=None):
        if not self.can_checkout():
            raise ValidationError('Cannot checkout this reservation.')

        self.status = 'checked_out'
        self.actual_checkout_at = timezone.now()
        if mileage:
            self.checkout_mileage = mileage
        self.save()

        self.vehicle.set_rented()

    def checkin(self, mileage=None):
        if not self.can_checkin():
            raise ValidationError('Cannot checkin this reservation.')

        self.status = 'completed'
        self.actual_checkin_at = timezone.now()
        if mileage:
            self.checkin_mileage = mileage
            if self.checkout_mileage:
                self.vehicle.mileage = mileage
                self.vehicle.save(update_fields=['mileage'])
        self.save()

        self.vehicle.set_available()

    def cancel(self):
        if not self.can_cancel():
            raise ValidationError('Cannot cancel this reservation.')

        self.status = 'cancelled'
        self.save()

    @classmethod
    def check_availability(cls, vehicle, start_date, end_date, exclude_pk=None):
        query = cls.objects.filter(
            vehicle=vehicle,
            status__in=['pending', 'confirmed', 'checked_out'],
            start_date__lt=end_date,
            end_date__gt=start_date,
        )
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)
        return not query.exists()


class ReservationExtra(TenantModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ['tenant', 'name']

    def __str__(self):
        return f'{self.name} (${self.daily_price}/day)'
