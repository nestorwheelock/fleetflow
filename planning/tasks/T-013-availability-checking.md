# T-013: Availability Checking Logic

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Implement vehicle availability checking for reservations
**Related Story**: S-003 (Reservation Calendar System)

## Constraints
**Allowed File Paths**:
- /apps/reservations/models.py
- /apps/reservations/services.py
- /apps/vehicles/models.py

## Deliverables
- [ ] Availability checking method on Reservation model
- [ ] Date range overlap detection
- [ ] Vehicle status consideration
- [ ] Multiple vehicle availability query
- [ ] Availability service layer

## Technical Specifications

### Availability Check Method
```python
class Reservation(models.Model):
    @classmethod
    def check_availability(cls, vehicle, start_date, end_date, exclude_id=None):
        """
        Check if a vehicle is available for the given date range.

        Args:
            vehicle: Vehicle instance or ID
            start_date: Requested pickup date
            end_date: Requested return date
            exclude_id: Reservation ID to exclude (for edits)

        Returns:
            bool: True if available, False if conflicts exist
        """
        conflicting = cls.objects.filter(
            vehicle=vehicle,
            status__in=['pending', 'confirmed', 'in_progress'],
            pickup_date__lt=end_date,
            return_date__gt=start_date
        )

        if exclude_id:
            conflicting = conflicting.exclude(pk=exclude_id)

        return not conflicting.exists()

    @classmethod
    def get_conflicts(cls, vehicle, start_date, end_date, exclude_id=None):
        """Return conflicting reservations for error messaging."""
        conflicting = cls.objects.filter(
            vehicle=vehicle,
            status__in=['pending', 'confirmed', 'in_progress'],
            pickup_date__lt=end_date,
            return_date__gt=start_date
        )

        if exclude_id:
            conflicting = conflicting.exclude(pk=exclude_id)

        return conflicting
```

### Availability Service
```python
# apps/reservations/services.py

from datetime import date, timedelta
from apps.vehicles.models import Vehicle
from apps.reservations.models import Reservation

class AvailabilityService:
    @staticmethod
    def get_available_vehicles(start_date, end_date, category=None):
        """Get all vehicles available for date range."""
        vehicles = Vehicle.objects.filter(status='available')

        if category:
            vehicles = vehicles.filter(category=category)

        # Exclude vehicles with conflicting reservations
        booked_vehicle_ids = Reservation.objects.filter(
            status__in=['pending', 'confirmed', 'in_progress'],
            pickup_date__lt=end_date,
            return_date__gt=start_date
        ).values_list('vehicle_id', flat=True)

        return vehicles.exclude(id__in=booked_vehicle_ids)

    @staticmethod
    def get_vehicle_availability_calendar(vehicle, start_date, end_date):
        """Get daily availability for a vehicle in date range."""
        reservations = Reservation.objects.filter(
            vehicle=vehicle,
            status__in=['pending', 'confirmed', 'in_progress'],
            pickup_date__lte=end_date,
            return_date__gte=start_date
        )

        calendar = {}
        current = start_date
        while current <= end_date:
            calendar[current] = {
                'available': True,
                'reservation': None
            }
            for res in reservations:
                if res.pickup_date <= current < res.return_date:
                    calendar[current] = {
                        'available': False,
                        'reservation': res
                    }
                    break
            current += timedelta(days=1)

        return calendar
```

### Edge Cases to Handle
- Same-day pickup and return
- Back-to-back reservations (same return/pickup date)
- Maintenance windows blocking availability
- Time-based conflicts (pickup/return times)

## Definition of Done
- [ ] Availability check returns correct results
- [ ] Overlap detection works for all edge cases
- [ ] Service methods tested with various scenarios
- [ ] Performance acceptable for large date ranges
- [ ] Tests written and passing (>95% coverage)
