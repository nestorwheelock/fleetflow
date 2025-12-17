# T-018: Charge Calculation Logic

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Implement pricing and charge calculation for reservations
**Related Story**: S-004 (Rental Workflow)

## Constraints
**Allowed File Paths**:
- /apps/reservations/models.py
- /apps/reservations/services.py
- /apps/reservations/pricing.py

## Deliverables
- [ ] Base rental calculation (daily/weekly/monthly rates)
- [ ] Tax calculation
- [ ] Extra mileage charges
- [ ] Fuel charges
- [ ] Late return fees
- [ ] Add-on pricing
- [ ] Deposit calculation

## Technical Specifications

### Pricing Configuration
```python
# apps/reservations/pricing.py

from decimal import Decimal
from dataclasses import dataclass

@dataclass
class PricingConfig:
    """Configurable pricing parameters."""
    TAX_RATE = Decimal('0.08')  # 8% tax
    MILEAGE_LIMIT_PER_DAY = 150  # miles
    EXTRA_MILEAGE_RATE = Decimal('0.25')  # per mile
    FUEL_PRICE_PER_GALLON = Decimal('4.50')
    ESTIMATED_TANK_SIZE = 15  # gallons
    LATE_FEE_PER_HOUR = Decimal('15.00')
    LATE_FEE_MAX_HOURS = 3  # After this, charge full day
    CLEANING_FEE = Decimal('75.00')

    # Insurance options
    INSURANCE_BASIC_DAILY = Decimal('10.00')
    INSURANCE_PREMIUM_DAILY = Decimal('18.00')

    # Add-ons
    GPS_DAILY = Decimal('5.00')
    CHILD_SEAT_DAILY = Decimal('8.00')
    ADDITIONAL_DRIVER_DAILY = Decimal('10.00')
    ROADSIDE_ASSISTANCE_DAILY = Decimal('5.00')
```

### Pricing Calculator
```python
# apps/reservations/services.py

from decimal import Decimal
from datetime import timedelta
from .pricing import PricingConfig

class PricingCalculator:
    def __init__(self, reservation):
        self.reservation = reservation
        self.config = PricingConfig()

    def calculate_base_rate(self):
        """Calculate base rental rate based on duration."""
        days = self.reservation.duration_days
        vehicle = self.reservation.vehicle

        if days >= 30 and vehicle.monthly_rate:
            # Monthly rate
            months = days // 30
            remaining_days = days % 30
            return (vehicle.monthly_rate * months) + (vehicle.daily_rate * remaining_days)
        elif days >= 7 and vehicle.weekly_rate:
            # Weekly rate
            weeks = days // 7
            remaining_days = days % 7
            return (vehicle.weekly_rate * weeks) + (vehicle.daily_rate * remaining_days)
        else:
            # Daily rate
            return vehicle.daily_rate * days

    def calculate_add_ons(self, add_ons=None):
        """Calculate cost of selected add-ons."""
        if not add_ons:
            add_ons = self.reservation.add_ons.all() if hasattr(self.reservation, 'add_ons') else []

        days = self.reservation.duration_days
        total = Decimal('0')

        add_on_rates = {
            'gps': self.config.GPS_DAILY,
            'child_seat': self.config.CHILD_SEAT_DAILY,
            'additional_driver': self.config.ADDITIONAL_DRIVER_DAILY,
            'roadside_assistance': self.config.ROADSIDE_ASSISTANCE_DAILY,
            'insurance_basic': self.config.INSURANCE_BASIC_DAILY,
            'insurance_premium': self.config.INSURANCE_PREMIUM_DAILY,
        }

        for add_on in add_ons:
            rate = add_on_rates.get(add_on.add_on_type, Decimal('0'))
            total += rate * days

        return total

    def calculate_subtotal(self):
        """Calculate subtotal before tax."""
        return self.calculate_base_rate() + self.calculate_add_ons()

    def calculate_tax(self, subtotal=None):
        """Calculate tax amount."""
        if subtotal is None:
            subtotal = self.calculate_subtotal()
        return subtotal * self.config.TAX_RATE

    def calculate_total(self):
        """Calculate total with tax."""
        subtotal = self.calculate_subtotal()
        tax = self.calculate_tax(subtotal)
        return subtotal + tax

    def calculate_deposit(self):
        """Calculate required deposit."""
        return self.reservation.vehicle.deposit_amount

    def calculate_extra_mileage(self, miles_driven):
        """Calculate extra mileage charges."""
        days = self.reservation.duration_days or 1
        allowed_miles = days * self.config.MILEAGE_LIMIT_PER_DAY
        extra_miles = max(0, miles_driven - allowed_miles)
        return extra_miles * self.config.EXTRA_MILEAGE_RATE

    def calculate_fuel_charge(self, pickup_level, return_level):
        """Calculate fuel shortage charge."""
        levels = {'full': 1, '3/4': 0.75, '1/2': 0.5, '1/4': 0.25, 'empty': 0}
        pickup_val = levels.get(pickup_level, 1)
        return_val = levels.get(return_level, 1)

        if return_val < pickup_val:
            gallons_short = (pickup_val - return_val) * self.config.ESTIMATED_TANK_SIZE
            return Decimal(str(gallons_short)) * self.config.FUEL_PRICE_PER_GALLON
        return Decimal('0')

    def calculate_late_fee(self, hours_late):
        """Calculate late return fee."""
        if hours_late <= 0:
            return Decimal('0')

        if hours_late <= self.config.LATE_FEE_MAX_HOURS:
            return self.config.LATE_FEE_PER_HOUR * hours_late
        else:
            return self.reservation.daily_rate

    def get_price_breakdown(self):
        """Get complete price breakdown for display."""
        base_rate = self.calculate_base_rate()
        add_ons = self.calculate_add_ons()
        subtotal = base_rate + add_ons
        tax = self.calculate_tax(subtotal)
        total = subtotal + tax
        deposit = self.calculate_deposit()

        return {
            'days': self.reservation.duration_days,
            'daily_rate': self.reservation.vehicle.daily_rate,
            'base_rate': base_rate,
            'add_ons': add_ons,
            'subtotal': subtotal,
            'tax_rate': self.config.TAX_RATE * 100,  # As percentage
            'tax_amount': tax,
            'total': total,
            'deposit': deposit,
            'amount_due': total + deposit,
        }
```

### Model Integration
```python
# apps/reservations/models.py

class Reservation(models.Model):
    # ... existing fields ...

    def calculate_total(self, save=True):
        """Calculate and optionally save total amounts."""
        from .services import PricingCalculator

        calculator = PricingCalculator(self)

        self.daily_rate = self.vehicle.daily_rate
        self.subtotal = calculator.calculate_subtotal()
        self.tax_amount = calculator.calculate_tax(self.subtotal)
        self.total_amount = self.subtotal + self.tax_amount
        self.deposit_amount = calculator.calculate_deposit()

        if save:
            self.save(update_fields=[
                'daily_rate', 'subtotal', 'tax_amount',
                'total_amount', 'deposit_amount'
            ])

        return self.total_amount

    def get_final_charges(self, return_mileage, fuel_level, hours_late=0):
        """Calculate additional charges at return."""
        from .services import PricingCalculator

        calculator = PricingCalculator(self)
        pickup_report = self.condition_reports.filter(report_type='pickup').first()

        miles_driven = return_mileage - (self.pickup_mileage or 0)
        pickup_fuel = pickup_report.fuel_level if pickup_report else 'full'

        return {
            'extra_mileage': calculator.calculate_extra_mileage(miles_driven),
            'fuel_charge': calculator.calculate_fuel_charge(pickup_fuel, fuel_level),
            'late_fee': calculator.calculate_late_fee(hours_late),
        }
```

## Definition of Done
- [ ] Base rate calculation works for daily/weekly/monthly
- [ ] Tax calculated correctly
- [ ] Add-on pricing accurate
- [ ] Extra mileage charges calculated
- [ ] Fuel charges calculated
- [ ] Late fees calculated
- [ ] Price breakdown available for display
- [ ] Tests written and passing (>95% coverage)
