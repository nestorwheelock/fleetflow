# T-015: Check-Out Workflow and Forms

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement vehicle pickup/check-out process
**Related Story**: S-004 (Rental Workflow)

## Constraints
**Allowed File Paths**:
- /apps/reservations/views.py
- /apps/reservations/forms.py
- /apps/reservations/urls.py
- /templates/reservations/checkout/*

## Deliverables
- [ ] Check-out wizard view (multi-step)
- [ ] Odometer recording form
- [ ] Fuel level recording
- [ ] Pre-rental condition checklist
- [ ] Photo upload for condition
- [ ] Contract generation trigger
- [ ] Status transition to 'in_progress'

## Technical Specifications

### Check-Out Wizard Steps
1. **Review** - Confirm reservation details and customer
2. **Condition** - Record vehicle condition and mileage
3. **Contract** - Review and sign rental agreement
4. **Complete** - Hand over keys, update status

### Check-Out Form
```python
# apps/reservations/forms.py

class CheckOutStep1Form(forms.Form):
    """Step 1: Review and confirm reservation."""
    customer_verified = forms.BooleanField(
        label="Customer ID verified",
        required=True
    )
    license_valid = forms.BooleanField(
        label="Driver's license is valid and not expired",
        required=True
    )
    payment_confirmed = forms.BooleanField(
        label="Payment/deposit confirmed",
        required=True
    )

class CheckOutStep2Form(forms.ModelForm):
    """Step 2: Vehicle condition at pickup."""
    class Meta:
        model = Reservation
        fields = ['pickup_mileage']

    fuel_level = forms.ChoiceField(
        choices=[
            ('full', 'Full'),
            ('3/4', '3/4'),
            ('1/2', '1/2'),
            ('1/4', '1/4'),
            ('empty', 'Empty'),
        ],
        initial='full'
    )

    exterior_condition = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Note any existing damage or issues"
    )

    interior_clean = forms.BooleanField(
        label="Interior is clean",
        initial=True
    )

    all_keys_provided = forms.IntegerField(
        label="Number of keys provided",
        initial=2,
        min_value=1
    )

    # Checklist items
    spare_tire_present = forms.BooleanField(initial=True, required=False)
    jack_present = forms.BooleanField(initial=True, required=False)
    registration_present = forms.BooleanField(initial=True, required=False)
    insurance_card_present = forms.BooleanField(initial=True, required=False)
    owners_manual_present = forms.BooleanField(initial=True, required=False)

class CheckOutStep3Form(forms.Form):
    """Step 3: Contract signing."""
    terms_accepted = forms.BooleanField(
        label="Customer accepts rental terms and conditions",
        required=True
    )
    signature_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
```

### Check-Out View
```python
# apps/reservations/views.py

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from formtools.wizard.views import SessionWizardView

CHECKOUT_FORMS = [
    ('review', CheckOutStep1Form),
    ('condition', CheckOutStep2Form),
    ('contract', CheckOutStep3Form),
]

class CheckOutWizardView(LoginRequiredMixin, SessionWizardView):
    template_name = 'reservations/checkout/wizard.html'
    form_list = CHECKOUT_FORMS

    def dispatch(self, request, *args, **kwargs):
        self.reservation = get_object_or_404(
            Reservation,
            pk=kwargs['pk'],
            status='confirmed'
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = self.reservation
        context['step_titles'] = ['Review', 'Condition', 'Contract', 'Complete']
        return context

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step == 'condition':
            kwargs['instance'] = self.reservation
        return kwargs

    def done(self, form_list, **kwargs):
        # Process all form data
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)

        # Update reservation
        self.reservation.pickup_mileage = form_data['pickup_mileage']
        self.reservation.actual_pickup = timezone.now()
        self.reservation.status = 'in_progress'
        self.reservation.save()

        # Create condition report
        ConditionReport.objects.create(
            reservation=self.reservation,
            report_type='pickup',
            mileage=form_data['pickup_mileage'],
            fuel_level=form_data['fuel_level'],
            exterior_notes=form_data.get('exterior_condition', ''),
            keys_count=form_data['all_keys_provided'],
            created_by=self.request.user
        )

        # Update vehicle status
        self.reservation.vehicle.status = 'rented'
        self.reservation.vehicle.save()

        # Generate contract if signature provided
        if form_data.get('signature_data'):
            from apps.contracts.services import ContractService
            ContractService.generate_contract(
                self.reservation,
                signature_data=form_data['signature_data']
            )

        messages.success(
            self.request,
            f'Vehicle checked out successfully. Reservation #{self.reservation.confirmation_number}'
        )
        return redirect('reservation_detail', pk=self.reservation.pk)
```

### URL Configuration
```python
# apps/reservations/urls.py

urlpatterns += [
    path('<int:pk>/checkout/', CheckOutWizardView.as_view(), name='reservation_checkout'),
]
```

## Definition of Done
- [ ] Multi-step checkout wizard works
- [ ] Mileage and fuel recorded correctly
- [ ] Condition checklist captured
- [ ] Contract generated with signature
- [ ] Reservation status updated to 'in_progress'
- [ ] Vehicle status updated to 'rented'
- [ ] Tests written and passing (>95% coverage)
