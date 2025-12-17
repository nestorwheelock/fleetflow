from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from apps.tenants.models import TenantModel


class VehicleCategory(TenantModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Vehicle Categories'
        unique_together = ['tenant', 'name']
        ordering = ['name']

    def __str__(self):
        return self.name


class Vehicle(TenantModel):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
        ('unavailable', 'Unavailable'),
    ]

    TRANSMISSION_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    ]

    FUEL_CHOICES = [
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]

    category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles'
    )
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20)
    vin = models.CharField(max_length=17, unique=True)
    color = models.CharField(max_length=30, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    weekly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    monthly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    mileage = models.PositiveIntegerField(default=0)
    seats = models.PositiveSmallIntegerField(default=5)
    doors = models.PositiveSmallIntegerField(default=4)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='automatic')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='gasoline')

    features = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    insurance_policy = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['tenant', 'license_plate']
        ordering = ['make', 'model', 'year']

    def __str__(self):
        return f'{self.year} {self.make} {self.model} ({self.license_plate})'

    def is_available(self):
        return self.status == 'available'

    def set_rented(self):
        self.status = 'rented'
        self.save(update_fields=['status'])

    def set_available(self):
        self.status = 'available'
        self.save(update_fields=['status'])

    def set_maintenance(self):
        self.status = 'maintenance'
        self.save(update_fields=['status'])


class VehiclePhoto(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='vehicle_photos/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            VehiclePhoto.objects.filter(vehicle=self.vehicle, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Photo for {self.vehicle}'
