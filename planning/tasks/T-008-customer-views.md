# T-008: Customer CRUD Views

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Create staff-facing customer management views
**Related Story**: S-002 (Customer Management)

## Constraints
**Allowed File Paths**:
- /apps/customers/views.py
- /apps/customers/urls.py
- /apps/customers/forms.py
- /templates/customers/*
- /config/urls.py

## Deliverables
- [ ] Customer list view with search
- [ ] Customer detail view with rental history
- [ ] Customer create/edit forms
- [ ] Customer delete with confirmation
- [ ] Templates with Tailwind CSS

## Technical Specifications

### Views
```python
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        flag = self.request.GET.get('flag')
        verified = self.request.GET.get('verified')
        # Apply filters...
        return queryset

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rental_history'] = self.object.reservations.order_by('-created_at')[:10]
        context['documents'] = self.object.documents.all()
        return context
```

### URL Patterns
```python
urlpatterns = [
    path('', CustomerListView.as_view(), name='customer_list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('create/', CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_update'),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),
]
```

## Definition of Done
- [ ] List view with search and filters
- [ ] Detail view shows all customer info
- [ ] Rental history displayed
- [ ] CRUD operations work
- [ ] Templates are responsive
- [ ] Tests written and passing (>95% coverage)
