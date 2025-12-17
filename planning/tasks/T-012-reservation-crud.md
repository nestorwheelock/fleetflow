# T-012: Reservation CRUD Operations

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Create views for managing reservations
**Related Story**: S-003 (Reservation Calendar System)

## Constraints
**Allowed File Paths**:
- /apps/reservations/views.py
- /apps/reservations/forms.py
- /apps/reservations/urls.py
- /templates/reservations/*

## Deliverables
- [ ] Reservation list view
- [ ] Reservation detail view
- [ ] Create reservation form (multi-step)
- [ ] Edit reservation
- [ ] Cancel reservation with reason
- [ ] Reservation search

## Technical Specifications

### Create Reservation Form
Multi-step wizard:
1. Select customer (search existing or create new)
2. Select vehicle (filter by availability)
3. Select dates and times
4. Add extras/add-ons
5. Review pricing and confirm

### Views
```python
class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.confirmation_number = generate_confirmation()
        form.instance.calculate_total()
        return super().form_valid(form)

class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'reservations/reservation_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_modify'] = self.object.status in ['pending', 'confirmed']
        context['contract'] = self.object.contracts.first()
        return context

class ReservationCancelView(LoginRequiredMixin, UpdateView):
    model = Reservation
    fields = ['notes']
    template_name = 'reservations/reservation_cancel.html'

    def form_valid(self, form):
        form.instance.status = 'cancelled'
        # Calculate refund based on policy
        return super().form_valid(form)
```

## Definition of Done
- [ ] List view with search/filter
- [ ] Detail view shows all reservation info
- [ ] Create form works with validation
- [ ] Edit updates reservation correctly
- [ ] Cancel prompts for reason
- [ ] Tests written and passing (>95% coverage)
