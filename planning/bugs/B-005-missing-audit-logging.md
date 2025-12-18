# B-005: Missing Audit Logging for Various Actions

**Severity**: Medium
**Affected Component**: Audit/Activity Logging System
**Discovered**: 2025-12-18

## Bug Description

The audit logging system (ActivityLog) is not capturing all user actions in the application. Specifically, vehicle photo uploads and potentially other actions are not being logged, making it difficult to track who performed what actions and when.

## Steps to Reproduce

1. Log in to the dashboard
2. Navigate to a vehicle detail page
3. Upload photos to the vehicle
4. Go to the Activity Log page
5. Observe that photo uploads are not logged

## Expected Behavior

All user actions should be logged in the ActivityLog, including:
- Vehicle photo uploads/deletions
- Customer document uploads
- Condition report photo uploads
- Status changes
- Any CRUD operations on any model

## Actual Behavior

Photo uploads and other actions are not appearing in the Activity Log.

## Environment

- Django: 6.0
- Python: 3.12

## Root Cause Analysis

The `log_activity()` helper function exists in `apps/tenants/models.py:292` but is not being called from:
- Vehicle photo upload views
- Customer document upload views
- Other API endpoints that modify data

## Proposed Fix

1. Add audit logging to all photo/document upload endpoints
2. Add 'upload' and 'delete' to ACTION_CHOICES in ActivityLog model
3. Consider creating a mixin or decorator to automatically log actions
4. Add comprehensive audit logging to all CreateView, UpdateView, DeleteView classes

## Files to Modify

- `apps/tenants/models.py` - Add 'upload' action type
- `apps/fleet/views.py` - Add logging to photo upload
- `apps/dashboard/views.py` - Add logging to various views
- Consider creating `apps/tenants/audit.py` for centralized audit utilities

## Acceptance Criteria

- [ ] All vehicle photo uploads are logged
- [ ] All customer document uploads are logged
- [ ] All CRUD operations on models are logged
- [ ] Activity Log UI shows all actions with correct details
- [ ] Tests verify audit logging works for all operations
