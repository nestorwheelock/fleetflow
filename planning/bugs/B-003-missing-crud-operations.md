# B-003: Missing CRUD Operations in Dashboard

**Severity**: Critical
**Affected Component**: Dashboard / All Entities
**Discovered**: December 2025

## Bug Description

The dashboard UI is missing Create, Update, and Delete operations for most entities. Only Vehicles have full CRUD implemented. This makes the application unusable for day-to-day operations.

## Current State

| Entity | List | Create | Detail | Edit | Delete |
|--------|------|--------|--------|------|--------|
| Vehicles | ✓ | ✓ | ✓ | ✓ | ✗ |
| Customers | ✓ | ✗ | ✓ | ✗ | ✗ |
| Reservations | ✓ | ✗ | ✓ | ✗ | ✗ |
| Contracts | ✓ | auto | ✓ | N/A | N/A |

## Steps to Reproduce

1. Log in to FleetFlow dashboard
2. Navigate to Customers - no "Add Customer" button
3. Navigate to Reservations - no "New Reservation" button
4. On any detail page - no Edit or Delete buttons

## Expected Behavior

- All entities should have Create, Read, Update, Delete operations
- List views should have "Add New" buttons
- Detail views should have "Edit" and "Delete" buttons
- Forms should validate and save data

## Fix Required

### Customers (Priority: High)
- [ ] Create view and form template (`/dashboard/customers/create/`)
- [ ] Edit view and form template (`/dashboard/customers/<pk>/edit/`)
- [ ] Delete confirmation and action
- [ ] Add buttons to list and detail templates

### Reservations (Priority: High)
- [ ] Create view and form template (`/dashboard/reservations/create/`)
- [ ] Edit view and form template (`/dashboard/reservations/<pk>/edit/`)
- [ ] Cancel action (soft delete via status change)
- [ ] Add buttons to list and detail templates
- [ ] Vehicle availability check in form

### Vehicles (Priority: Medium)
- [ ] Delete confirmation and action
- [ ] Add delete button to detail template

## Technical Requirements

- Use Django class-based views (CreateView, UpdateView, DeleteView)
- Tenant isolation on all operations
- Form validation with error messages
- Success/error flash messages
- Redirect to list after save/delete

## Related Files

- `apps/dashboard/urls.py` - Add new routes
- `apps/dashboard/views.py` - Add new view classes
- `templates/dashboard/customers/form.html` - Create template
- `templates/dashboard/reservations/form.html` - Create template
- Update list.html and detail.html for each entity

## API Endpoints (Already Exist)

The REST APIs already support full CRUD:
- POST `/api/customers/` - Create customer
- PATCH `/api/customers/<id>/` - Update customer
- DELETE `/api/customers/<id>/` - Delete customer
- POST `/api/reservations/` - Create reservation
- PATCH `/api/reservations/<id>/` - Update reservation
- POST `/api/reservations/<id>/cancel/` - Cancel reservation

The dashboard UI needs to be built to use these or implement Django form views.
