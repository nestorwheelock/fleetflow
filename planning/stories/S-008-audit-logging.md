# S-008: Audit Logging for User Activity

**Story Type**: User Story
**Priority**: High
**Estimate**: 2 days
**Sprint**: Sprint 3
**Status**: Pending

## User Story
**As a** tenant owner/manager
**I want to** see a complete audit trail of all user actions in the system
**So that** I can track accountability, investigate issues, and maintain compliance

## Background
Car rental businesses need accountability for every action taken in the system. When a vehicle is damaged, a reservation is modified, or a customer record is updated, management needs to know who did it and when.

## Acceptance Criteria

### Audit Fields on Records
- [ ] When I view any record, I can see who created it
- [ ] When I view any record, I can see who last updated it
- [ ] Checkout/checkin operations show which employee performed them

### Activity Log
- [ ] When any CRUD operation occurs, it is logged with the user who performed it
- [ ] When I view the activity log, I can filter by:
  - User/employee
  - Action type (create, update, delete, checkout, checkin)
  - Record type (vehicle, customer, reservation, contract)
  - Date range
- [ ] When I view a specific record, I can see its activity history

### Tracked Actions
- [ ] Create operations log: user, timestamp, record created
- [ ] Update operations log: user, timestamp, fields changed (before/after)
- [ ] Delete operations log: user, timestamp, record details at deletion
- [ ] Checkout operations log: user, timestamp, reservation details
- [ ] Checkin operations log: user, timestamp, reservation details
- [ ] Status changes log: user, timestamp, old status → new status

## Definition of Done
- [ ] AuditMixin created with created_by/updated_by fields
- [ ] ActivityLog model implemented
- [ ] All tenant models inherit audit fields
- [ ] Views auto-populate audit fields on save
- [ ] Activity log dashboard page created
- [ ] Record detail pages show activity history
- [ ] Tests written for audit functionality (>95% coverage)
- [ ] Migration created and applied

## Technical Notes

### AuditMixin (Base Class)
```python
class AuditMixin(models.Model):
    created_by = ForeignKey(User, null=True, on_delete=SET_NULL, related_name='+')
    updated_by = ForeignKey(User, null=True, on_delete=SET_NULL, related_name='+')

    class Meta:
        abstract = True
```

### ActivityLog Model
```python
class ActivityLog(models.Model):
    tenant = ForeignKey(Tenant, on_delete=CASCADE)
    user = ForeignKey(User, null=True, on_delete=SET_NULL)
    action = CharField(choices=ACTION_CHOICES)  # create, update, delete, checkout, checkin
    model_name = CharField(max_length=100)
    object_id = PositiveIntegerField()
    object_repr = CharField(max_length=255)
    changes = JSONField(blank=True, null=True)  # {field: {old: x, new: y}}
    timestamp = DateTimeField(auto_now_add=True)
    ip_address = GenericIPAddressField(null=True, blank=True)
```

### Mixin for Views
```python
class AuditViewMixin:
    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
```

## Related Issues
- GitHub Issue #2: feat: Add audit logging for user activity

## Dependencies
- None (foundational feature)

## Out of Scope (Future)
- IP address geolocation
- Export audit logs to CSV/PDF
- Email alerts for specific actions
- Data retention policies
