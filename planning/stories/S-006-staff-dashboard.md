# S-006: Staff Dashboard

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 3 days
**Sprint**: Epoch 1
**Status**: PARTIAL (Core complete, enhancements pending)

## User Story
**As a** rental business owner
**I want to** see an overview dashboard
**So that** I can monitor daily operations at a glance

## Acceptance Criteria
- [x] Can see today's scheduled pickups with customer/vehicle info
- [x] Can see today's scheduled returns with customer/vehicle info
- [x] Can see count of current rentals in progress
- [x] Can see count of available vehicles
- [ ] Can see overdue returns with alert styling
- [x] Can see recent reservations (last 5)
- [x] Quick action buttons for common tasks
- [ ] Dashboard refreshes data automatically
- [ ] **NEW**: Upcoming Returns section showing returns for next 7 days (Issue #8)

## Definition of Done
- [x] Dashboard view with all widgets
- [x] Today's pickups list with details
- [x] Today's returns list with details
- [x] Stats cards (available, rented, overdue)
- [x] Recent reservations list
- [x] Quick action shortcuts working
- [ ] Auto-refresh every 5 minutes
- [x] Tests written and passing (>95% coverage)
- [x] Documentation updated

## Related Tasks
- T-022: Dashboard view and template (Done)
- T-023: Dashboard widgets and stats (Done)
- T-024: Quick action shortcuts (Done)

## Pending Enhancements
- Issue #8: Add Upcoming Returns view to dashboard
- Auto-refresh feature
- Overdue returns alert styling

## Notes
- Dashboard is the landing page after login
- Alerts for overdue returns prominently displayed
- Quick actions: New Reservation, Add Customer, Add Vehicle
- Mobile-responsive layout
- Activity Log accessible from dashboard
