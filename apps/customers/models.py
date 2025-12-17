from django.db import models
from django.core.validators import EmailValidator
from datetime import date

from apps.tenants.models import TenantModel


class Customer(TenantModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    phone_secondary = models.CharField(max_length=30, blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='USA')

    date_of_birth = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    license_state = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    license_image_front = models.ImageField(upload_to='customer_licenses/', blank=True, null=True)
    license_image_back = models.ImageField(upload_to='customer_licenses/', blank=True, null=True)

    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['tenant', 'email']
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return (today - self.date_of_birth).days // 365

    def is_license_expired(self):
        if not self.license_expiry:
            return False
        return self.license_expiry < date.today()

    def is_eligible_to_rent(self):
        if self.is_blacklisted:
            return False
        if self.age is not None and self.age < 18:
            return False
        return True

    def get_rental_history(self):
        from apps.reservations.models import Reservation
        return Reservation.objects.filter(customer=self).order_by('-start_date')

    @property
    def total_rentals(self):
        from apps.reservations.models import Reservation
        return Reservation.objects.filter(customer=self).count()


class CustomerDocument(TenantModel):
    DOCUMENT_TYPES = [
        ('license_front', 'License Front'),
        ('license_back', 'License Back'),
        ('passport', 'Passport'),
        ('id_card', 'ID Card'),
        ('insurance', 'Insurance Card'),
        ('other', 'Other'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='customer_documents/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.customer} - {self.get_document_type_display()}'
