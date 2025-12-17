# T-006: Customer Model and Migrations

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Create Customer model with profile and license info
**Related Story**: S-002 (Customer Management)

## Constraints
**Allowed File Paths**:
- /apps/customers/*
- /config/settings/*.py (for INSTALLED_APPS)

**Forbidden Paths**: None

## Deliverables
- [ ] customers Django app created
- [ ] Customer model with all fields
- [ ] CustomerFlag model (or choices)
- [ ] Database migrations created
- [ ] Model methods for common operations
- [ ] Model validation for license

## Technical Specifications

### Customer Model Fields
```python
class Customer(models.Model):
    # Link to Django User (optional)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # Contact Info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    # Address
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='USA')

    # Driver's License
    license_number = models.CharField(max_length=50)
    license_state = models.CharField(max_length=50)
    license_expiry = models.DateField()
    date_of_birth = models.DateField()

    # Status
    is_verified = models.BooleanField(default=False)
    flag = models.CharField(choices=FLAG_CHOICES, default='regular')

    # Notes
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def license_is_expired(self):
        return self.license_expiry < date.today()

    @property
    def license_expires_soon(self):
        return self.license_expiry < date.today() + timedelta(days=30)
```

### Customer Flags
- regular: Normal customer
- vip: VIP customer (priority service)
- new: First-time renter
- banned: Not allowed to rent
- blacklisted: Severe issues

## Definition of Done
- [ ] Model created with all fields
- [ ] Migrations run successfully
- [ ] Properties work correctly
- [ ] License validation (expiry date)
- [ ] __str__ returns full name
- [ ] Tests written and passing (>95% coverage)
