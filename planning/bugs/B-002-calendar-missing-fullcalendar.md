# B-002: Calendar View Missing FullCalendar JS Library

**Severity**: High
**Affected Component**: Reservations / Calendar View
**Discovered**: December 2025

## Bug Description

The reservation calendar view at `/dashboard/reservations/calendar/` displays a message "Calendar view requires FullCalendar JS library" instead of showing an actual calendar. The FullCalendar JavaScript library is not included in the template.

## Steps to Reproduce

1. Log in to FleetFlow
2. Navigate to Reservations > Calendar
3. Or directly visit `/dashboard/reservations/calendar/`
4. See placeholder message instead of functional calendar

## Expected Behavior

- Interactive calendar showing reservations
- Ability to view reservations by day/week/month
- Click on dates to see reservation details
- Visual representation of vehicle availability

## Actual Behavior

- Page displays: "Calendar view requires FullCalendar JS library"
- No functional calendar rendered
- API endpoint `/api/reservations/calendar/` exists but UI doesn't use it

## Root Cause

The calendar template (`templates/dashboard/reservations/calendar.html`) does not include the FullCalendar library or JavaScript to initialize it and fetch data from the API.

## Fix Required

1. Add FullCalendar CDN or npm package to the calendar template
2. Initialize FullCalendar with proper configuration
3. Connect to `/api/reservations/calendar/` API endpoint
4. Style calendar to match FleetFlow design (Tailwind)
5. Add click handlers for reservation details

## Technical Details

**API Endpoint**: `/api/reservations/calendar/`
- Returns reservations in a date range
- Query params: `start`, `end` (dates)
- Returns: list of reservations with vehicle, customer, dates

**FullCalendar Requirements**:
- FullCalendar v6.x (latest)
- Day/Week/Month views
- Event click handling
- Responsive design

## Environment

- Django: 5.x
- Python: 3.12
- Browser: All modern browsers

## Related Files

- `templates/dashboard/reservations/calendar.html` - Needs FullCalendar integration
- `apps/reservations/views.py` - Calendar API view exists
- `apps/dashboard/views.py` - Calendar template view
