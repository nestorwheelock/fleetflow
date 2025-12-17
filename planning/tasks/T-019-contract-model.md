# T-019: Contract Model and Template

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Create contract model and rental agreement template
**Related Story**: S-005 (Basic Contract Generation)

## Constraints
**Allowed File Paths**:
- /apps/contracts/* (new app)
- /config/settings/*.py (for INSTALLED_APPS)

## Deliverables
- [ ] contracts Django app created
- [ ] Contract model with all fields
- [ ] Rental agreement template (HTML/text)
- [ ] Terms and conditions content
- [ ] Signature storage

## Technical Specifications

### Contract Model
```python
# apps/contracts/models.py

from django.db import models
from django.conf import settings
import uuid

class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_signature', 'Pending Signature'),
        ('signed', 'Signed'),
        ('voided', 'Voided'),
    ]

    # Reference
    contract_number = models.CharField(max_length=30, unique=True, editable=False)
    reservation = models.ForeignKey(
        'reservations.Reservation',
        on_delete=models.CASCADE,
        related_name='contracts'
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Content
    terms_version = models.CharField(max_length=20, default='1.0')
    rental_terms = models.TextField()  # Snapshot of terms at signing
    special_conditions = models.TextField(blank=True)

    # Pricing snapshot (in case rates change)
    daily_rate_snapshot = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount_snapshot = models.DecimalField(max_digits=10, decimal_places=2)

    # Signature
    signature_data = models.TextField(blank=True)  # Base64 encoded signature image
    signature_type = models.CharField(
        max_length=20,
        choices=[('drawn', 'Drawn'), ('typed', 'Typed')],
        blank=True
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    signer_name = models.CharField(max_length=100, blank=True)
    signer_ip_address = models.GenericIPAddressField(null=True, blank=True)
    signer_user_agent = models.TextField(blank=True)

    # Generated document
    document_pdf = models.FileField(
        upload_to='contracts/%Y/%m/',
        null=True,
        blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract {self.contract_number}"

    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = self._generate_contract_number()
        super().save(*args, **kwargs)

    def _generate_contract_number(self):
        """Generate unique contract number."""
        from datetime import datetime
        prefix = datetime.now().strftime('%Y%m')
        unique_part = uuid.uuid4().hex[:8].upper()
        return f"CTR-{prefix}-{unique_part}"

    @property
    def is_signed(self):
        return self.status == 'signed' and self.signed_at is not None

    def mark_signed(self, signature_data, ip_address=None, user_agent=None):
        """Mark contract as signed with signature data."""
        from django.utils import timezone

        self.signature_data = signature_data
        self.signed_at = timezone.now()
        self.signer_ip_address = ip_address
        self.signer_user_agent = user_agent or ''
        self.signer_name = self.reservation.customer.full_name
        self.status = 'signed'
        self.save()


class TermsAndConditions(models.Model):
    """Store versioned terms and conditions."""
    version = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Terms and Conditions"
        ordering = ['-effective_date']

    def __str__(self):
        return f"Terms v{self.version} ({self.effective_date})"

    @classmethod
    def get_current(cls):
        """Get the current active terms."""
        return cls.objects.filter(is_active=True).order_by('-effective_date').first()
```

### Default Terms Template
```python
# apps/contracts/templates/contracts/terms_default.txt

RENTAL AGREEMENT TERMS AND CONDITIONS

1. RENTAL PERIOD
The rental period begins at the pickup date and time specified and ends at the
return date and time specified. Late returns will incur additional charges.

2. MILEAGE
Your rental includes {{ mileage_limit }} miles per day. Additional miles will
be charged at ${{ extra_mileage_rate }} per mile.

3. FUEL POLICY
The vehicle is provided with a full tank of fuel and must be returned with a
full tank. If returned with less fuel, you will be charged ${{ fuel_rate }}
per gallon plus a refueling service fee.

4. INSURANCE AND LIABILITY
- Basic coverage: $500 deductible for damages
- Premium coverage: $0 deductible for damages
You are responsible for all damages not covered by your selected coverage.

5. PROHIBITED USES
The vehicle may not be used for:
- Off-road driving
- Racing or speed testing
- Towing or pushing
- Transporting hazardous materials
- Illegal activities
- Subleasing to others

6. DRIVER REQUIREMENTS
- Must be at least 25 years of age
- Must possess a valid driver's license
- Must be listed on this rental agreement
- Additional drivers must be registered and approved

7. ACCIDENTS AND DAMAGE
In case of accident or damage:
- Contact local authorities if required
- Do not admit fault
- Contact our office immediately at {{ company_phone }}
- Document the incident with photos

8. LATE RETURNS
- Up to 3 hours late: ${{ late_hourly_fee }} per hour
- More than 3 hours late: Full additional day rate
- Failure to return: Reported to authorities

9. DEPOSIT
A security deposit of ${{ deposit_amount }} will be authorized on your payment
method. This will be released upon satisfactory return of the vehicle.

10. CANCELLATION POLICY
- More than 48 hours before pickup: Full refund
- 24-48 hours before pickup: 50% refund
- Less than 24 hours: No refund

By signing this agreement, I acknowledge that I have read, understand, and
agree to all terms and conditions stated above.
```

### Contract Admin
```python
# apps/contracts/admin.py

from django.contrib import admin
from .models import Contract, TermsAndConditions

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'reservation', 'status', 'signed_at', 'created_at']
    list_filter = ['status', 'created_at', 'signed_at']
    search_fields = ['contract_number', 'reservation__confirmation_number',
                     'reservation__customer__first_name']
    readonly_fields = ['contract_number', 'created_at', 'updated_at',
                       'signed_at', 'signer_ip_address']

    fieldsets = (
        ('Reference', {
            'fields': ('contract_number', 'reservation', 'status')
        }),
        ('Content', {
            'fields': ('terms_version', 'rental_terms', 'special_conditions')
        }),
        ('Pricing', {
            'fields': ('daily_rate_snapshot', 'total_amount_snapshot')
        }),
        ('Signature', {
            'fields': ('signature_type', 'signer_name', 'signed_at',
                       'signer_ip_address'),
            'classes': ('collapse',)
        }),
        ('Document', {
            'fields': ('document_pdf',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )

@admin.register(TermsAndConditions)
class TermsAdmin(admin.ModelAdmin):
    list_display = ['version', 'title', 'effective_date', 'is_active']
    list_filter = ['is_active', 'effective_date']
```

## Definition of Done
- [ ] Contract model created with all fields
- [ ] Terms and conditions model created
- [ ] Admin interface configured
- [ ] Default terms template created
- [ ] Signature storage works
- [ ] Contract versioning works
- [ ] Tests written and passing (>95% coverage)
