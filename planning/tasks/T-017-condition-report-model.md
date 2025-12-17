# T-017: Condition Report Model

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Create model to track vehicle condition at pickup and return
**Related Story**: S-004 (Rental Workflow)

## Constraints
**Allowed File Paths**:
- /apps/reservations/models.py
- /apps/reservations/admin.py

## Deliverables
- [ ] ConditionReport model
- [ ] ConditionPhoto model for damage photos
- [ ] Admin interface for condition reports
- [ ] Comparison between pickup and return

## Technical Specifications

### ConditionReport Model
```python
class ConditionReport(models.Model):
    REPORT_TYPES = [
        ('pickup', 'Pickup Inspection'),
        ('return', 'Return Inspection'),
    ]

    FUEL_LEVELS = [
        ('full', 'Full'),
        ('3/4', '3/4'),
        ('1/2', '1/2'),
        ('1/4', '1/4'),
        ('empty', 'Empty'),
    ]

    CONDITION_RATINGS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='condition_reports'
    )
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)

    # Vehicle state
    mileage = models.PositiveIntegerField()
    fuel_level = models.CharField(max_length=10, choices=FUEL_LEVELS)

    # Condition ratings
    exterior_rating = models.CharField(
        max_length=20,
        choices=CONDITION_RATINGS,
        default='good'
    )
    interior_rating = models.CharField(
        max_length=20,
        choices=CONDITION_RATINGS,
        default='good'
    )

    # Detailed notes
    exterior_notes = models.TextField(blank=True)
    interior_notes = models.TextField(blank=True)

    # Checklist items (stored as JSON)
    checklist = models.JSONField(default=dict, blank=True)
    # Example: {"spare_tire": true, "jack": true, "registration": true}

    # Keys
    keys_count = models.PositiveSmallIntegerField(default=2)

    # Damage tracking
    has_damage = models.BooleanField(default=False)
    damage_description = models.TextField(blank=True)
    damage_locations = models.JSONField(default=list, blank=True)
    # Example: ["front", "left_side"]

    estimated_repair_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['reservation', 'report_type']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.reservation.confirmation_number}"

    @property
    def is_pickup(self):
        return self.report_type == 'pickup'

    @property
    def is_return(self):
        return self.report_type == 'return'


class ConditionPhoto(models.Model):
    PHOTO_TYPES = [
        ('front', 'Front'),
        ('rear', 'Rear'),
        ('left', 'Left Side'),
        ('right', 'Right Side'),
        ('interior', 'Interior'),
        ('odometer', 'Odometer'),
        ('damage', 'Damage'),
        ('other', 'Other'),
    ]

    condition_report = models.ForeignKey(
        ConditionReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo = models.ImageField(upload_to='condition_reports/%Y/%m/')
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPES)
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['photo_type', 'uploaded_at']

    def __str__(self):
        return f"{self.get_photo_type_display()} - {self.condition_report}"
```

### Comparison Utility
```python
class ConditionReport(models.Model):
    # ... fields above ...

    @classmethod
    def compare_reports(cls, reservation):
        """Compare pickup and return condition reports."""
        try:
            pickup = cls.objects.get(reservation=reservation, report_type='pickup')
            return_report = cls.objects.get(reservation=reservation, report_type='return')
        except cls.DoesNotExist:
            return None

        comparison = {
            'miles_driven': return_report.mileage - pickup.mileage,
            'fuel_difference': cls._compare_fuel(pickup.fuel_level, return_report.fuel_level),
            'exterior_changed': pickup.exterior_rating != return_report.exterior_rating,
            'interior_changed': pickup.interior_rating != return_report.interior_rating,
            'new_damage': return_report.has_damage and not pickup.has_damage,
            'keys_difference': pickup.keys_count - return_report.keys_count,
        }

        return comparison

    @staticmethod
    def _compare_fuel(pickup_level, return_level):
        levels = {'full': 1, '3/4': 0.75, '1/2': 0.5, '1/4': 0.25, 'empty': 0}
        pickup_val = levels.get(pickup_level, 1)
        return_val = levels.get(return_level, 1)
        return return_val - pickup_val  # Negative means less fuel returned
```

### Admin Configuration
```python
# apps/reservations/admin.py

class ConditionPhotoInline(admin.TabularInline):
    model = ConditionPhoto
    extra = 0

@admin.register(ConditionReport)
class ConditionReportAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'report_type', 'mileage', 'fuel_level',
                    'has_damage', 'created_at']
    list_filter = ['report_type', 'has_damage', 'fuel_level', 'created_at']
    search_fields = ['reservation__confirmation_number',
                     'reservation__customer__first_name']
    readonly_fields = ['created_at', 'created_by']
    inlines = [ConditionPhotoInline]

    fieldsets = (
        ('Reservation', {
            'fields': ('reservation', 'report_type')
        }),
        ('Vehicle State', {
            'fields': ('mileage', 'fuel_level', 'keys_count')
        }),
        ('Condition', {
            'fields': ('exterior_rating', 'exterior_notes',
                       'interior_rating', 'interior_notes')
        }),
        ('Damage', {
            'fields': ('has_damage', 'damage_description',
                       'damage_locations', 'estimated_repair_cost')
        }),
        ('Checklist', {
            'fields': ('checklist',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by')
        }),
    )
```

## Definition of Done
- [ ] ConditionReport model created
- [ ] ConditionPhoto model for images
- [ ] Admin interface configured
- [ ] Pickup/return comparison works
- [ ] Photos upload correctly
- [ ] Tests written and passing (>95% coverage)
