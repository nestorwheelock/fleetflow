# T-010: Reservation Model and Migrations

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Create Reservation model for booking management
**Related Story**: S-003 (Reservation Calendar System)

## Constraints
**Allowed File Paths**:
- /apps/reservations/*
- /config/settings/*.py (for INSTALLED_APPS)

## Deliverables
- [ ] reservations Django app created
- [ ] Reservation model with all fields
- [ ] ReservationAddOn model (optional extras)
- [ ] Database migrations
- [ ] Pricing calculation methods
- [ ] Availability checking method

## Technical Specifications

### Reservation Model
```python
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Reference
    confirmation_number = models.CharField(max_length=20, unique=True)

    # Relationships
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='reservations')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='reservations')

    # Dates
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    return_date = models.DateField()
    return_time = models.TimeField()

    # Actual dates (filled at check-out/check-in)
    actual_pickup = models.DateTimeField(null=True, blank=True)
    actual_return = models.DateTimeField(null=True, blank=True)

    # Pricing
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Mileage
    pickup_mileage = models.PositiveIntegerField(null=True, blank=True)
    return_mileage = models.PositiveIntegerField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    @property
    def duration_days(self):
        return (self.return_date - self.pickup_date).days

    @property
    def miles_driven(self):
        if self.return_mileage and self.pickup_mileage:
            return self.return_mileage - self.pickup_mileage
        return None

    def calculate_total(self):
        # Calculate based on duration, add-ons, tax
        pass

    @classmethod
    def check_availability(cls, vehicle, start_date, end_date, exclude_id=None):
        # Check for overlapping reservations
        pass
```

## Definition of Done
- [ ] Model created with all fields
- [ ] Migrations run successfully
- [ ] Pricing calculations work
- [ ] Availability check works
- [ ] Confirmation number auto-generated
- [ ] Tests written and passing (>95% coverage)
