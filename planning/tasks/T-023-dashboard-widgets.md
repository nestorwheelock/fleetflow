# T-023: Dashboard Widgets and Stats

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Create reusable dashboard widgets and statistics components
**Related Story**: S-006 (Staff Dashboard)

## Constraints
**Allowed File Paths**:
- /apps/dashboard/widgets.py
- /apps/dashboard/templatetags/*
- /templates/dashboard/widgets/*
- /static/js/dashboard.js

## Deliverables
- [ ] Reusable widget components
- [ ] Vehicle status widget
- [ ] Revenue summary widget
- [ ] Recent activity feed
- [ ] Calendar mini-view
- [ ] HTMX-powered live updates

## Technical Specifications

### Widget Base Classes
```python
# apps/dashboard/widgets.py

from abc import ABC, abstractmethod
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

class DashboardWidget(ABC):
    """Base class for dashboard widgets."""
    template_name = None
    title = ""
    refresh_interval = 60  # seconds

    @abstractmethod
    def get_data(self):
        """Return widget data."""
        pass

    def render(self, request=None):
        """Render widget to HTML."""
        context = {
            'widget': self,
            'data': self.get_data(),
            'title': self.title,
        }
        return render_to_string(self.template_name, context, request=request)


class VehicleStatusWidget(DashboardWidget):
    """Shows vehicle fleet status breakdown."""
    template_name = 'dashboard/widgets/vehicle_status.html'
    title = "Fleet Status"

    def get_data(self):
        from apps.vehicles.models import Vehicle

        stats = Vehicle.objects.values('status').annotate(
            count=Count('id')
        )

        status_map = {
            'available': {'label': 'Available', 'color': 'green'},
            'rented': {'label': 'Rented', 'color': 'blue'},
            'maintenance': {'label': 'In Service', 'color': 'yellow'},
            'retired': {'label': 'Retired', 'color': 'gray'},
        }

        result = []
        total = 0
        for stat in stats:
            status_info = status_map.get(stat['status'], {})
            result.append({
                'status': stat['status'],
                'count': stat['count'],
                'label': status_info.get('label', stat['status']),
                'color': status_info.get('color', 'gray'),
            })
            total += stat['count']

        # Calculate percentages
        for item in result:
            item['percentage'] = (item['count'] / total * 100) if total > 0 else 0

        return {'items': result, 'total': total}


class RevenueWidget(DashboardWidget):
    """Shows revenue statistics."""
    template_name = 'dashboard/widgets/revenue.html'
    title = "Revenue"

    def get_data(self):
        from apps.reservations.models import Reservation
        from django.db.models import Sum

        today = timezone.now().date()

        # Today's revenue
        today_revenue = Reservation.objects.filter(
            status='completed',
            actual_return__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # This week
        week_start = today - timedelta(days=today.weekday())
        week_revenue = Reservation.objects.filter(
            status='completed',
            actual_return__date__gte=week_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # This month
        month_start = today.replace(day=1)
        month_revenue = Reservation.objects.filter(
            status='completed',
            actual_return__date__gte=month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Active rentals value
        active_value = Reservation.objects.filter(
            status='in_progress'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        return {
            'today': today_revenue,
            'week': week_revenue,
            'month': month_revenue,
            'active': active_value,
        }


class RecentActivityWidget(DashboardWidget):
    """Shows recent system activity."""
    template_name = 'dashboard/widgets/recent_activity.html'
    title = "Recent Activity"

    def get_data(self):
        from apps.reservations.models import Reservation

        activities = []

        # Recent reservations
        recent_reservations = Reservation.objects.order_by('-created_at')[:5]
        for res in recent_reservations:
            activities.append({
                'type': 'reservation',
                'icon': '📅',
                'message': f'New reservation #{res.confirmation_number}',
                'detail': f'{res.customer.full_name} - {res.vehicle}',
                'timestamp': res.created_at,
                'link': f'/reservations/{res.pk}/'
            })

        # Recent check-outs
        recent_checkouts = Reservation.objects.filter(
            status='in_progress',
            actual_pickup__isnull=False
        ).order_by('-actual_pickup')[:3]
        for res in recent_checkouts:
            activities.append({
                'type': 'checkout',
                'icon': '🚗',
                'message': f'Vehicle checked out',
                'detail': f'{res.vehicle} to {res.customer.full_name}',
                'timestamp': res.actual_pickup,
                'link': f'/reservations/{res.pk}/'
            })

        # Recent returns
        recent_returns = Reservation.objects.filter(
            status='completed',
            actual_return__isnull=False
        ).order_by('-actual_return')[:3]
        for res in recent_returns:
            activities.append({
                'type': 'checkin',
                'icon': '✅',
                'message': f'Vehicle returned',
                'detail': f'{res.vehicle} from {res.customer.full_name}',
                'timestamp': res.actual_return,
                'link': f'/reservations/{res.pk}/'
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        return activities[:10]


class CalendarMiniWidget(DashboardWidget):
    """Mini calendar showing upcoming reservations."""
    template_name = 'dashboard/widgets/calendar_mini.html'
    title = "Upcoming"

    def get_data(self):
        from apps.reservations.models import Reservation

        today = timezone.now().date()
        next_week = today + timedelta(days=7)

        upcoming = Reservation.objects.filter(
            pickup_date__gte=today,
            pickup_date__lte=next_week,
            status__in=['pending', 'confirmed']
        ).order_by('pickup_date', 'pickup_time')[:10]

        # Group by date
        by_date = {}
        for res in upcoming:
            date_key = res.pickup_date
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(res)

        return {
            'by_date': by_date,
            'count': upcoming.count()
        }
```

### Widget Templates
```html
<!-- templates/dashboard/widgets/vehicle_status.html -->
<div class="bg-white rounded-lg shadow p-4"
     hx-get="{% url 'widget_vehicle_status' %}"
     hx-trigger="every 60s"
     hx-swap="outerHTML">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>

    <div class="space-y-3">
        {% for item in data.items %}
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <span class="w-3 h-3 rounded-full bg-{{ item.color }}-500 mr-2"></span>
                <span class="text-gray-700">{{ item.label }}</span>
            </div>
            <div class="flex items-center">
                <span class="font-medium">{{ item.count }}</span>
                <span class="text-gray-500 text-sm ml-1">({{ item.percentage|floatformat:0 }}%)</span>
            </div>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-{{ item.color }}-500 h-2 rounded-full"
                 style="width: {{ item.percentage }}%"></div>
        </div>
        {% endfor %}
    </div>

    <div class="mt-4 pt-4 border-t text-center">
        <span class="text-2xl font-bold">{{ data.total }}</span>
        <span class="text-gray-600 text-sm ml-1">Total Vehicles</span>
    </div>
</div>

<!-- templates/dashboard/widgets/revenue.html -->
<div class="bg-white rounded-lg shadow p-4">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>

    <div class="grid grid-cols-2 gap-4">
        <div class="text-center p-3 bg-green-50 rounded">
            <p class="text-sm text-gray-600">Today</p>
            <p class="text-xl font-bold text-green-600">${{ data.today|floatformat:2 }}</p>
        </div>
        <div class="text-center p-3 bg-blue-50 rounded">
            <p class="text-sm text-gray-600">This Week</p>
            <p class="text-xl font-bold text-blue-600">${{ data.week|floatformat:2 }}</p>
        </div>
        <div class="text-center p-3 bg-purple-50 rounded">
            <p class="text-sm text-gray-600">This Month</p>
            <p class="text-xl font-bold text-purple-600">${{ data.month|floatformat:2 }}</p>
        </div>
        <div class="text-center p-3 bg-yellow-50 rounded">
            <p class="text-sm text-gray-600">Active Rentals</p>
            <p class="text-xl font-bold text-yellow-600">${{ data.active|floatformat:2 }}</p>
        </div>
    </div>
</div>

<!-- templates/dashboard/widgets/recent_activity.html -->
<div class="bg-white rounded-lg shadow p-4">
    <h3 class="text-lg font-semibold mb-4">{{ title }}</h3>

    <div class="space-y-3 max-h-80 overflow-y-auto">
        {% for activity in data %}
        <a href="{{ activity.link }}" class="block p-2 hover:bg-gray-50 rounded">
            <div class="flex items-start">
                <span class="text-xl mr-3">{{ activity.icon }}</span>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900">{{ activity.message }}</p>
                    <p class="text-sm text-gray-500 truncate">{{ activity.detail }}</p>
                </div>
                <span class="text-xs text-gray-400">
                    {{ activity.timestamp|timesince }} ago
                </span>
            </div>
        </a>
        {% empty %}
        <p class="text-gray-500 text-center py-4">No recent activity</p>
        {% endfor %}
    </div>
</div>
```

### Widget View Endpoints
```python
# apps/dashboard/views.py

from django.http import HttpResponse
from .widgets import VehicleStatusWidget, RevenueWidget, RecentActivityWidget

class WidgetView(LoginRequiredMixin, View):
    """Base view for HTMX widget updates."""
    widget_class = None

    def get(self, request):
        widget = self.widget_class()
        return HttpResponse(widget.render(request))

class VehicleStatusWidgetView(WidgetView):
    widget_class = VehicleStatusWidget

class RevenueWidgetView(WidgetView):
    widget_class = RevenueWidget

class RecentActivityWidgetView(WidgetView):
    widget_class = RecentActivityWidget
```

### URL Configuration
```python
# apps/dashboard/urls.py

urlpatterns += [
    path('widgets/vehicle-status/', VehicleStatusWidgetView.as_view(), name='widget_vehicle_status'),
    path('widgets/revenue/', RevenueWidgetView.as_view(), name='widget_revenue'),
    path('widgets/activity/', RecentActivityWidgetView.as_view(), name='widget_activity'),
]
```

## Definition of Done
- [ ] Widget base class created
- [ ] Vehicle status widget works
- [ ] Revenue widget shows correct data
- [ ] Activity feed displays recent items
- [ ] Calendar mini-view functional
- [ ] HTMX live updates working
- [ ] Tests written and passing (>95% coverage)
