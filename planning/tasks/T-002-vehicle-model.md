# T-002: Vehicle Model and Migrations

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Create Vehicle model with all required fields
**Related Story**: S-001 (Vehicle Fleet Management)

## Constraints
**Allowed File Paths**:
- /apps/vehicles/*
- /config/settings/*.py (for INSTALLED_APPS)

**Forbidden Paths**: None

## Deliverables
- [ ] vehicles Django app created
- [ ] Vehicle model with all fields
- [ ] VehicleCategory model (or choices)
- [ ] Database migrations created
- [ ] Model methods for common operations
- [ ] Model validation

## Technical Specifications

### Vehicle Model Fields
```python
class Vehicle(models.Model):
    # Basic Info
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vin = models.CharField(max_length=17, unique=True)
    license_plate = models.CharField(max_length=15, unique=True)
    color = models.CharField(max_length=30)

    # Specifications
    category = models.CharField(choices=CATEGORY_CHOICES)
    transmission = models.CharField(choices=TRANSMISSION_CHOICES)
    fuel_type = models.CharField(choices=FUEL_CHOICES)
    seats = models.PositiveIntegerField(default=5)
    mileage = models.PositiveIntegerField(default=0)

    # Pricing
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    mileage_limit_per_day = models.PositiveIntegerField(default=150)
    extra_mile_rate = models.DecimalField(default=0.25)
    deposit_amount = models.DecimalField(default=200.00)

    # Status
    status = models.CharField(choices=STATUS_CHOICES, default='available')

    # Features (JSON or M2M)
    features = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
```

### Choices
- CATEGORY: sedan, suv, truck, van, luxury, economy
- STATUS: available, rented, maintenance, reserved, archived
- TRANSMISSION: automatic, manual
- FUEL_TYPE: gasoline, diesel, hybrid, electric

## Definition of Done
- [ ] Model created with all fields
- [ ] Migrations run successfully
- [ ] Model can be created in Django shell
- [ ] Validation works (VIN format, year range, etc.)
- [ ] __str__ method returns useful representation
- [ ] Tests written and passing (>95% coverage)
