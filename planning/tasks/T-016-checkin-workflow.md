# T-016: Check-In Workflow and Forms

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement vehicle return/check-in process
**Related Story**: S-004 (Rental Workflow)

## Constraints
**Allowed File Paths**:
- /apps/reservations/views.py
- /apps/reservations/forms.py
- /apps/reservations/urls.py
- /templates/reservations/checkin/*

## Deliverables
- [ ] Check-in wizard view (multi-step)
- [ ] Return odometer recording
- [ ] Post-rental condition inspection
- [ ] Damage documentation with photos
- [ ] Final charge calculation
- [ ] Receipt generation
- [ ] Status transition to 'completed'

## Technical Specifications

### Check-In Wizard Steps
1. **Inspect** - Record return condition and mileage
2. **Damages** - Document any new damage
3. **Charges** - Calculate and review final charges
4. **Complete** - Generate receipt, update status

### Check-In Forms
```python
# apps/reservations/forms.py

class CheckInStep1Form(forms.ModelForm):
    """Step 1: Return inspection."""
    class Meta:
        model = Reservation
        fields = ['return_mileage']

    fuel_level = forms.ChoiceField(
        choices=[
            ('full', 'Full'),
            ('3/4', '3/4'),
            ('1/2', '1/2'),
            ('1/4', '1/4'),
            ('empty', 'Empty'),
        ]
    )

    exterior_condition = forms.ChoiceField(
        choices=[
            ('excellent', 'Excellent - No issues'),
            ('good', 'Good - Minor wear'),
            ('fair', 'Fair - Some issues noted'),
            ('poor', 'Poor - Significant damage'),
        ]
    )

    interior_condition = forms.ChoiceField(
        choices=[
            ('clean', 'Clean'),
            ('acceptable', 'Acceptable'),
            ('dirty', 'Dirty - Cleaning required'),
            ('damaged', 'Damaged'),
        ]
    )

    all_keys_returned = forms.IntegerField(
        label="Number of keys returned",
        min_value=0
    )

    condition_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

class CheckInStep2Form(forms.Form):
    """Step 2: Damage documentation."""
    has_new_damage = forms.BooleanField(
        label="New damage found",
        required=False
    )

    damage_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Describe any new damage in detail"
    )

    damage_location = forms.MultipleChoiceField(
        choices=[
            ('front', 'Front'),
            ('rear', 'Rear'),
            ('left_side', 'Left Side'),
            ('right_side', 'Right Side'),
            ('roof', 'Roof'),
            ('interior', 'Interior'),
            ('windshield', 'Windshield'),
            ('tires', 'Tires/Wheels'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    estimated_repair_cost = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False
    )

class CheckInStep3Form(forms.Form):
    """Step 3: Final charges review."""
    extra_mileage_charge = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0,
        disabled=True
    )

    fuel_charge = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0,
        disabled=True
    )

    late_return_charge = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0,
        disabled=True
    )

    cleaning_charge = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0
    )

    damage_charge = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0
    )

    adjustment = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0,
        help_text="Positive for additional charge, negative for credit"
    )

    adjustment_reason = forms.CharField(
        max_length=200,
        required=False
    )

    customer_agrees = forms.BooleanField(
        label="Customer agrees to final charges",
        required=True
    )
```

### Check-In View
```python
class CheckInWizardView(LoginRequiredMixin, SessionWizardView):
    template_name = 'reservations/checkin/wizard.html'
    form_list = [
        ('inspect', CheckInStep1Form),
        ('damages', CheckInStep2Form),
        ('charges', CheckInStep3Form),
    ]

    def dispatch(self, request, *args, **kwargs):
        self.reservation = get_object_or_404(
            Reservation,
            pk=kwargs['pk'],
            status='in_progress'
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)

        if step == 'charges':
            # Pre-calculate charges
            charges = self.calculate_charges()
            initial.update(charges)

        return initial

    def calculate_charges(self):
        """Calculate extra charges based on inspection data."""
        form_data = self.get_all_cleaned_data()
        charges = {
            'extra_mileage_charge': Decimal('0'),
            'fuel_charge': Decimal('0'),
            'late_return_charge': Decimal('0'),
        }

        # Extra mileage calculation
        if form_data.get('return_mileage') and self.reservation.pickup_mileage:
            miles_driven = form_data['return_mileage'] - self.reservation.pickup_mileage
            days = self.reservation.duration_days or 1
            allowed_miles = days * 150  # 150 miles/day limit
            extra_miles = max(0, miles_driven - allowed_miles)
            charges['extra_mileage_charge'] = extra_miles * Decimal('0.25')

        # Fuel charge
        fuel_levels = {'full': 1, '3/4': 0.75, '1/2': 0.5, '1/4': 0.25, 'empty': 0}
        pickup_level = 1  # Assumed full at pickup
        return_level = fuel_levels.get(form_data.get('fuel_level', 'full'), 1)
        if return_level < pickup_level:
            # Estimate: 15 gallon tank at $4.50/gallon
            gallons_short = (pickup_level - return_level) * 15
            charges['fuel_charge'] = Decimal(str(gallons_short * 4.50))

        # Late return
        if self.reservation.actual_return:
            scheduled_return = datetime.combine(
                self.reservation.return_date,
                self.reservation.return_time
            )
            if timezone.now() > scheduled_return:
                hours_late = (timezone.now() - scheduled_return).seconds // 3600
                if hours_late <= 3:
                    charges['late_return_charge'] = hours_late * Decimal('15')
                else:
                    charges['late_return_charge'] = self.reservation.daily_rate

        return charges

    def done(self, form_list, **kwargs):
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)

        # Update reservation
        self.reservation.return_mileage = form_data['return_mileage']
        self.reservation.actual_return = timezone.now()
        self.reservation.status = 'completed'

        # Calculate final total
        extra_charges = (
            form_data.get('extra_mileage_charge', 0) +
            form_data.get('fuel_charge', 0) +
            form_data.get('late_return_charge', 0) +
            form_data.get('cleaning_charge', 0) +
            form_data.get('damage_charge', 0) +
            form_data.get('adjustment', 0)
        )
        self.reservation.total_amount += extra_charges
        self.reservation.save()

        # Create return condition report
        ConditionReport.objects.create(
            reservation=self.reservation,
            report_type='return',
            mileage=form_data['return_mileage'],
            fuel_level=form_data['fuel_level'],
            exterior_notes=form_data.get('condition_notes', ''),
            has_damage=form_data.get('has_new_damage', False),
            damage_description=form_data.get('damage_description', ''),
            created_by=self.request.user
        )

        # Update vehicle status
        self.reservation.vehicle.status = 'available'
        self.reservation.vehicle.mileage = form_data['return_mileage']
        self.reservation.vehicle.save()

        # Generate receipt
        from apps.contracts.services import ContractService
        ContractService.generate_receipt(self.reservation)

        messages.success(
            self.request,
            f'Vehicle checked in successfully. Final total: ${self.reservation.total_amount}'
        )
        return redirect('reservation_detail', pk=self.reservation.pk)
```

## Definition of Done
- [ ] Multi-step check-in wizard works
- [ ] Return mileage and condition recorded
- [ ] Damage documentation with photos
- [ ] Extra charges calculated correctly
- [ ] Final receipt generated
- [ ] Reservation status updated to 'completed'
- [ ] Vehicle status updated to 'available'
- [ ] Tests written and passing (>95% coverage)
