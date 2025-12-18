from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator
from datetime import date

from apps.tenants.models import TenantModel, AuditMixin


class Customer(TenantModel, AuditMixin):
    PHOTO_SOURCE_CHOICES = [
        ('license', 'From License'),
        ('upload', 'Manual Upload'),
    ]

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    phone_secondary = models.CharField(max_length=30, blank=True)

    # Profile photo (can come from license OCR or manual upload)
    profile_photo = models.ImageField(upload_to='customer_photos/', blank=True, null=True)
    profile_photo_source = models.CharField(
        max_length=20,
        choices=PHOTO_SOURCE_CHOICES,
        blank=True,
        help_text='Source of the profile photo'
    )

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='USA')

    date_of_birth = models.DateField(null=True, blank=True)

    # License information
    license_number = models.CharField(max_length=50, blank=True)
    license_state = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    license_issue_date = models.DateField(null=True, blank=True)
    license_class = models.CharField(max_length=20, blank=True, help_text='License class (A, B, C, CDL, etc.)')
    license_restrictions = models.CharField(max_length=200, blank=True, help_text='License restrictions')
    license_endorsements = models.CharField(max_length=200, blank=True, help_text='License endorsements')
    license_donor_status = models.BooleanField(null=True, blank=True, help_text='Organ donor status')
    license_image_front = models.ImageField(upload_to='customer_licenses/', blank=True, null=True)
    license_image_back = models.ImageField(upload_to='customer_licenses/', blank=True, null=True)

    # Physical characteristics (from license)
    gender = models.CharField(max_length=20, blank=True)
    height = models.CharField(max_length=20, blank=True, help_text="Height (e.g., 5'10\" or 178cm)")
    weight = models.CharField(max_length=20, blank=True, help_text='Weight (e.g., 180 lbs or 82kg)')
    eye_color = models.CharField(max_length=30, blank=True)
    hair_color = models.CharField(max_length=30, blank=True)

    # OCR metadata
    license_ocr_parsed_at = models.DateTimeField(null=True, blank=True)
    license_ocr_confidence = models.FloatField(null=True, blank=True, help_text='OCR confidence score (0.0-1.0)')

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


class CustomerInsurance(TenantModel):
    COVERAGE_TYPE_CHOICES = [
        ('liability', 'Liability Only'),
        ('collision', 'Collision'),
        ('comprehensive', 'Comprehensive'),
        ('full', 'Full Coverage'),
        ('other', 'Other'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='insurance_records')
    company_name = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    policyholder_name = models.CharField(max_length=200, blank=True)
    policyholder_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text='Relationship to customer (self, spouse, parent, etc.)'
    )
    coverage_type = models.CharField(
        max_length=20,
        choices=COVERAGE_TYPE_CHOICES,
        blank=True
    )
    covered_vehicles = models.JSONField(
        default=list,
        blank=True,
        help_text='List of covered vehicles [{year, make, model, vin}]'
    )
    agent_name = models.CharField(max_length=200, blank=True)
    agent_phone = models.CharField(max_length=30, blank=True)
    document = models.ForeignKey(
        CustomerDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='insurance_records'
    )
    insurance_card_image = models.ImageField(
        upload_to='customer_insurance/',
        blank=True,
        null=True
    )
    ocr_parsed_at = models.DateTimeField(null=True, blank=True)
    ocr_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text='OCR confidence score (0.0-1.0)'
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Customer insurance records'

    def __str__(self):
        return f'{self.customer} - {self.company_name} ({self.policy_number})'

    def is_expired(self):
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()

    def is_valid(self):
        if not self.effective_date or not self.expiration_date:
            return False
        today = date.today()
        return self.effective_date <= today <= self.expiration_date
