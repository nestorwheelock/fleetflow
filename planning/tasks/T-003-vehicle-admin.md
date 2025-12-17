# T-003: Vehicle Admin Interface

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Configure Django admin for vehicle management
**Related Story**: S-001 (Vehicle Fleet Management)

## Constraints
**Allowed File Paths**:
- /apps/vehicles/admin.py

**Forbidden Paths**: None

## Deliverables
- [ ] VehicleAdmin with list display
- [ ] Search and filter capabilities
- [ ] Inline for vehicle images
- [ ] Custom actions (mark available, mark maintenance)
- [ ] Fieldsets for organized form
- [ ] Read-only fields for computed values

## Technical Specifications

### Admin Configuration
```python
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'license_plate', 'category', 'status', 'daily_rate']
    list_filter = ['status', 'category', 'transmission', 'fuel_type']
    search_fields = ['make', 'model', 'vin', 'license_plate']
    list_editable = ['status']

    fieldsets = (
        ('Basic Information', {
            'fields': ('make', 'model', 'year', 'color')
        }),
        ('Identification', {
            'fields': ('vin', 'license_plate')
        }),
        ('Specifications', {
            'fields': ('category', 'transmission', 'fuel_type', 'seats', 'mileage')
        }),
        ('Pricing', {
            'fields': ('daily_rate', 'weekly_rate', 'monthly_rate',
                      'mileage_limit_per_day', 'extra_mile_rate', 'deposit_amount')
        }),
        ('Status & Features', {
            'fields': ('status', 'features', 'is_active')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
    inlines = [VehicleImageInline]
    actions = ['mark_available', 'mark_maintenance']
```

## Definition of Done
- [ ] Admin accessible at /admin/vehicles/vehicle/
- [ ] All CRUD operations work
- [ ] Filters and search work correctly
- [ ] Custom actions function properly
- [ ] Images can be added inline
- [ ] Documentation in code comments
