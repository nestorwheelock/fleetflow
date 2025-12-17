# T-014: Conflict Prevention System

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Prevent double-bookings and reservation conflicts
**Related Story**: S-003 (Reservation Calendar System)

## Constraints
**Allowed File Paths**:
- /apps/reservations/models.py
- /apps/reservations/forms.py
- /apps/reservations/validators.py

## Deliverables
- [ ] Model-level validation for conflicts
- [ ] Form validation for reservation creation
- [ ] Database constraint consideration
- [ ] Error messaging for conflicts
- [ ] Concurrent booking protection

## Technical Specifications

### Model Validation
```python
from django.core.exceptions import ValidationError

class Reservation(models.Model):
    def clean(self):
        super().clean()
        self._validate_dates()
        self._validate_availability()

    def _validate_dates(self):
        """Ensure return date is after pickup date."""
        if self.pickup_date and self.return_date:
            if self.return_date < self.pickup_date:
                raise ValidationError({
                    'return_date': 'Return date must be after pickup date.'
                })

            # Same day rental requires return time after pickup time
            if self.return_date == self.pickup_date:
                if self.return_time and self.pickup_time:
                    if self.return_time <= self.pickup_time:
                        raise ValidationError({
                            'return_time': 'Return time must be after pickup time for same-day rentals.'
                        })

    def _validate_availability(self):
        """Check for conflicting reservations."""
        if not self.vehicle or not self.pickup_date or not self.return_date:
            return

        if not self.check_availability(
            self.vehicle,
            self.pickup_date,
            self.return_date,
            exclude_id=self.pk
        ):
            conflicts = self.get_conflicts(
                self.vehicle,
                self.pickup_date,
                self.return_date,
                exclude_id=self.pk
            )
            conflict_info = ', '.join([
                f"#{c.confirmation_number} ({c.pickup_date} - {c.return_date})"
                for c in conflicts[:3]
            ])
            raise ValidationError({
                'vehicle': f'Vehicle is not available for selected dates. Conflicts: {conflict_info}'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

### Form Validation
```python
# apps/reservations/forms.py

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['vehicle', 'customer', 'pickup_date', 'pickup_time',
                  'return_date', 'return_time', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle')
        pickup_date = cleaned_data.get('pickup_date')
        return_date = cleaned_data.get('return_date')

        if vehicle and pickup_date and return_date:
            # Check vehicle status
            if vehicle.status != 'available':
                self.add_error('vehicle', f'Vehicle is currently {vehicle.get_status_display()}')

            # Check availability
            exclude_id = self.instance.pk if self.instance else None
            if not Reservation.check_availability(vehicle, pickup_date, return_date, exclude_id):
                self.add_error('vehicle', 'Vehicle is not available for selected dates.')

        return cleaned_data
```

### Concurrent Booking Protection
```python
from django.db import transaction
from django.db.models import Q

class ReservationCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        with transaction.atomic():
            # Lock the vehicle row to prevent race conditions
            vehicle = Vehicle.objects.select_for_update().get(
                pk=form.cleaned_data['vehicle'].pk
            )

            # Re-check availability inside transaction
            if not Reservation.check_availability(
                vehicle,
                form.cleaned_data['pickup_date'],
                form.cleaned_data['return_date']
            ):
                form.add_error('vehicle', 'Vehicle was just booked by another user.')
                return self.form_invalid(form)

            return super().form_valid(form)
```

### User-Friendly Error Messages
```python
# apps/reservations/validators.py

def get_availability_message(vehicle, start_date, end_date):
    """Generate helpful message about next available dates."""
    conflicts = Reservation.get_conflicts(vehicle, start_date, end_date)

    if not conflicts:
        return "Vehicle is available for selected dates."

    # Find next available window
    latest_conflict = max(conflicts, key=lambda r: r.return_date)
    next_available = latest_conflict.return_date

    return (
        f"Vehicle is booked until {next_available.strftime('%B %d, %Y')}. "
        f"Next available date: {next_available.strftime('%B %d, %Y')}"
    )
```

## Definition of Done
- [ ] Cannot create overlapping reservations
- [ ] Clear error messages for conflicts
- [ ] Race condition protection works
- [ ] Edit reservation respects conflicts
- [ ] Tests written and passing (>95% coverage)
