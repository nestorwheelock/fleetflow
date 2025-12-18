# B-007: Calendar Not Showing Reservations

**Severity**: High
**Affected Component**: Reservation Calendar
**Discovered**: 2025-12-18

## Bug Description

Reservations are not populating in the calendar view. The calendar displays but existing reservations do not appear as events.

## Steps to Reproduce

1. Log in to the dashboard
2. Create a reservation (or have existing reservations)
3. Navigate to the calendar view
4. Observe that reservations are not displayed

## Expected Behavior

All active reservations should appear on the calendar as events, showing:
- Customer name
- Vehicle
- Start and end dates
- Status indication (color coding)

## Actual Behavior

Calendar appears empty or reservations do not show.

## Root Cause Analysis

Possible causes:
1. Calendar API endpoint not returning reservations
2. JavaScript not properly fetching or rendering events
3. Tenant filtering issue - wrong tenant context
4. Date format mismatch between API and FullCalendar
5. Reservation query filtering out valid reservations

## Files to Investigate

- `apps/dashboard/views.py` - Calendar view and API endpoint
- `apps/reservations/views.py` - Reservation list/calendar API
- `templates/dashboard/reservations/calendar.html` - Calendar template
- `static/js/` - Calendar JavaScript

## Debugging Steps

1. Check browser console for JavaScript errors
2. Inspect network tab for API requests
3. Manually call calendar API to verify data
4. Check tenant context in view

## Acceptance Criteria

- [ ] Reservations appear on calendar
- [ ] Different status types have distinct colors
- [ ] Click on reservation shows details
- [ ] Calendar navigation works (prev/next month)
- [ ] Test coverage for calendar API
