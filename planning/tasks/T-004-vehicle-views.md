# T-004: Vehicle List/Detail Views

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Create staff-facing vehicle list and detail views
**Related Story**: S-001 (Vehicle Fleet Management)

## Constraints
**Allowed File Paths**:
- /apps/vehicles/views.py
- /apps/vehicles/urls.py
- /templates/vehicles/*
- /config/urls.py

**Forbidden Paths**: None

## Deliverables
- [ ] Vehicle list view with pagination
- [ ] Vehicle detail view
- [ ] Grid view option
- [ ] Filter by status, category
- [ ] Search functionality
- [ ] Create/Edit/Delete vehicle forms
- [ ] Templates with Tailwind CSS

## Technical Specifications

### Views
```python
# List view with filtering
class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        # Apply filters from GET params
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        # ... filter logic
        return queryset

# Detail view
class VehicleDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'vehicles/vehicle_detail.html'

# Create/Update views
class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
```

### URL Patterns
```python
urlpatterns = [
    path('', VehicleListView.as_view(), name='vehicle_list'),
    path('<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('create/', VehicleCreateView.as_view(), name='vehicle_create'),
    path('<int:pk>/edit/', VehicleUpdateView.as_view(), name='vehicle_update'),
    path('<int:pk>/delete/', VehicleDeleteView.as_view(), name='vehicle_delete'),
]
```

## Definition of Done
- [ ] List view shows all vehicles with pagination
- [ ] Filters work correctly
- [ ] Search works on make, model, plate
- [ ] Detail view shows all vehicle info
- [ ] CRUD operations work
- [ ] Templates are responsive
- [ ] Tests written and passing (>95% coverage)
