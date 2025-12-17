# T-011: Calendar View with FullCalendar.js

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement interactive reservation calendar
**Related Story**: S-003 (Reservation Calendar System)

## Constraints
**Allowed File Paths**:
- /apps/reservations/views.py
- /apps/reservations/urls.py
- /templates/reservations/*
- /static/js/*
- /static/css/*

## Deliverables
- [ ] Calendar page with FullCalendar.js
- [ ] Month/week/day views
- [ ] Reservations displayed as events
- [ ] Vehicle filter sidebar
- [ ] Category filter
- [ ] Click to create reservation
- [ ] Click event to view details

## Technical Specifications

### API Endpoint for Events
```python
# GET /api/reservations/events/
def reservation_events(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    vehicle_id = request.GET.get('vehicle')
    category = request.GET.get('category')

    reservations = Reservation.objects.filter(
        pickup_date__lte=end,
        return_date__gte=start
    )
    # Apply filters...

    events = []
    for res in reservations:
        events.append({
            'id': res.id,
            'title': f"{res.customer.full_name} - {res.vehicle}",
            'start': res.pickup_date.isoformat(),
            'end': res.return_date.isoformat(),
            'resourceId': res.vehicle_id,
            'color': get_status_color(res.status),
            'extendedProps': {
                'customer': res.customer.full_name,
                'vehicle': str(res.vehicle),
                'status': res.status,
            }
        })
    return JsonResponse(events, safe=False)
```

### FullCalendar Configuration
```javascript
const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    events: '/api/reservations/events/',
    eventClick: function(info) {
        // Open reservation detail modal
    },
    dateClick: function(info) {
        // Open new reservation form
    },
    editable: true,
    eventDrop: function(info) {
        // Update reservation dates via AJAX
    }
});
```

## Definition of Done
- [ ] Calendar displays correctly
- [ ] All view modes work (month/week/day)
- [ ] Reservations shown as colored events
- [ ] Filters work correctly
- [ ] Click events trigger appropriate actions
- [ ] Drag-and-drop reschedule works
- [ ] Tests written and passing (>95% coverage)
