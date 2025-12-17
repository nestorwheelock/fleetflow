# T-007: Customer Admin Interface

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Configure Django admin for customer management
**Related Story**: S-002 (Customer Management)

## Constraints
**Allowed File Paths**:
- /apps/customers/admin.py

## Deliverables
- [ ] CustomerAdmin with list display
- [ ] Search by name, email, phone, license
- [ ] Filter by flag, verified status
- [ ] Inline for customer documents
- [ ] Custom actions (verify, flag as VIP)

## Technical Specifications

### Admin Configuration
```python
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'flag', 'is_verified', 'license_status']
    list_filter = ['flag', 'is_verified', 'license_state']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'license_number']
    readonly_fields = ['created_at', 'updated_at', 'rental_count', 'lifetime_value']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country')
        }),
        ("Driver's License", {
            'fields': ('license_number', 'license_state', 'license_expiry', 'date_of_birth')
        }),
        ('Status', {
            'fields': ('is_verified', 'flag', 'notes')
        }),
        ('Statistics', {
            'fields': ('rental_count', 'lifetime_value'),
            'classes': ('collapse',)
        }),
    )

    inlines = [CustomerDocumentInline]
    actions = ['verify_customers', 'flag_as_vip', 'flag_as_banned']
```

## Definition of Done
- [ ] Admin accessible at /admin/customers/customer/
- [ ] All CRUD operations work
- [ ] Search and filters work correctly
- [ ] Custom actions function properly
- [ ] License status indicator (expired, expiring, valid)
