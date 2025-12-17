# T-022: Dashboard View and Template

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Create staff dashboard for daily operations overview
**Related Story**: S-006 (Staff Dashboard)

## Constraints
**Allowed File Paths**:
- /apps/dashboard/* (new app)
- /templates/dashboard/*
- /config/urls.py

## Deliverables
- [ ] Dashboard Django app
- [ ] Dashboard view with context data
- [ ] Main dashboard template
- [ ] Today's schedule section
- [ ] Statistics cards
- [ ] Quick actions section

## Technical Specifications

### Dashboard View
```python
# apps/dashboard/views.py

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta

from apps.vehicles.models import Vehicle
from apps.reservations.models import Reservation
from apps.customers.models import Customer

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Today's pickups
        context['todays_pickups'] = Reservation.objects.filter(
            pickup_date=today,
            status='confirmed'
        ).select_related('customer', 'vehicle').order_by('pickup_time')

        # Today's returns
        context['todays_returns'] = Reservation.objects.filter(
            return_date=today,
            status='in_progress'
        ).select_related('customer', 'vehicle').order_by('return_time')

        # Overdue returns
        context['overdue_returns'] = Reservation.objects.filter(
            return_date__lt=today,
            status='in_progress'
        ).select_related('customer', 'vehicle').order_by('return_date')

        # Vehicle statistics
        vehicle_stats = Vehicle.objects.aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(status='available')),
            rented=Count('id', filter=Q(status='rented')),
            maintenance=Count('id', filter=Q(status='maintenance')),
        )
        context['vehicle_stats'] = vehicle_stats

        # Current rentals in progress
        context['active_rentals'] = Reservation.objects.filter(
            status='in_progress'
        ).count()

        # Recent reservations
        context['recent_reservations'] = Reservation.objects.order_by(
            '-created_at'
        )[:5].select_related('customer', 'vehicle')

        # Week's revenue (completed reservations)
        week_ago = today - timedelta(days=7)
        context['weekly_revenue'] = Reservation.objects.filter(
            status='completed',
            actual_return__date__gte=week_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Alerts
        context['alerts'] = self._get_alerts(today)

        return context

    def _get_alerts(self, today):
        """Generate system alerts."""
        alerts = []

        # Overdue returns
        overdue_count = Reservation.objects.filter(
            return_date__lt=today,
            status='in_progress'
        ).count()
        if overdue_count:
            alerts.append({
                'type': 'danger',
                'icon': '🔴',
                'message': f'{overdue_count} overdue return(s)',
                'link': '?filter=overdue'
            })

        # Due today
        due_today = Reservation.objects.filter(
            return_date=today,
            status='in_progress'
        ).count()
        if due_today:
            alerts.append({
                'type': 'warning',
                'icon': '🟡',
                'message': f'{due_today} return(s) due today',
                'link': '?filter=due_today'
            })

        # Vehicles in maintenance
        in_maintenance = Vehicle.objects.filter(status='maintenance').count()
        if in_maintenance:
            alerts.append({
                'type': 'info',
                'icon': '🔵',
                'message': f'{in_maintenance} vehicle(s) in maintenance',
                'link': '/vehicles/?status=maintenance'
            })

        # Pending reservations needing confirmation
        pending = Reservation.objects.filter(status='pending').count()
        if pending:
            alerts.append({
                'type': 'warning',
                'icon': '🟡',
                'message': f'{pending} pending reservation(s)',
                'link': '/reservations/?status=pending'
            })

        return alerts
```

### Dashboard Template
```html
<!-- templates/dashboard/dashboard.html -->
{% extends "base.html" %}
{% load humanize %}

{% block title %}Dashboard - CarFlow{% endblock %}

{% block content %}
<div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-600">{{ today|date:"l, F j, Y" }}</p>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Today's Pickups -->
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
                <div class="p-3 rounded-full bg-blue-100 text-blue-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                </div>
                <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Today's Pickups</p>
                    <p class="text-2xl font-bold text-gray-900">{{ todays_pickups.count }}</p>
                </div>
            </div>
        </div>

        <!-- Today's Returns -->
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
                <div class="p-3 rounded-full bg-green-100 text-green-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
                <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Today's Returns</p>
                    <p class="text-2xl font-bold text-gray-900">{{ todays_returns.count }}</p>
                </div>
            </div>
        </div>

        <!-- Available Vehicles -->
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
                <div class="p-3 rounded-full bg-purple-100 text-purple-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10"/>
                    </svg>
                </div>
                <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Vehicles Available</p>
                    <p class="text-2xl font-bold text-gray-900">
                        {{ vehicle_stats.available }}/{{ vehicle_stats.total }}
                    </p>
                </div>
            </div>
        </div>

        <!-- Overdue -->
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center">
                <div class="p-3 rounded-full {% if overdue_returns %}bg-red-100 text-red-600{% else %}bg-gray-100 text-gray-600{% endif %}">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
                <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Overdue</p>
                    <p class="text-2xl font-bold {% if overdue_returns %}text-red-600{% else %}text-gray-900{% endif %}">
                        {{ overdue_returns.count }}
                    </p>
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Today's Schedule -->
        <div class="lg:col-span-2 bg-white rounded-lg shadow">
            <div class="p-4 border-b">
                <h2 class="text-lg font-semibold">Today's Schedule</h2>
            </div>
            <div class="p-4">
                <!-- Pickups -->
                <div class="mb-6">
                    <h3 class="text-sm font-medium text-gray-500 uppercase mb-3">
                        Pickups ({{ todays_pickups.count }})
                    </h3>
                    {% if todays_pickups %}
                    <div class="space-y-2">
                        {% for res in todays_pickups %}
                        <div class="flex items-center justify-between p-3 bg-blue-50 rounded">
                            <div class="flex items-center space-x-3">
                                <span class="text-sm font-medium text-blue-600">
                                    {{ res.pickup_time|time:"g:i A" }}
                                </span>
                                <span class="font-medium">{{ res.customer.full_name }}</span>
                                <span class="text-gray-600">{{ res.vehicle }}</span>
                            </div>
                            <a href="{% url 'reservation_detail' res.pk %}"
                               class="text-sm text-blue-600 hover:underline">
                                #{{ res.confirmation_number }}
                            </a>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-gray-500">No pickups scheduled for today</p>
                    {% endif %}
                </div>

                <!-- Returns -->
                <div>
                    <h3 class="text-sm font-medium text-gray-500 uppercase mb-3">
                        Returns ({{ todays_returns.count }})
                    </h3>
                    {% if todays_returns %}
                    <div class="space-y-2">
                        {% for res in todays_returns %}
                        <div class="flex items-center justify-between p-3 bg-green-50 rounded">
                            <div class="flex items-center space-x-3">
                                <span class="text-sm font-medium text-green-600">
                                    {{ res.return_time|time:"g:i A" }}
                                </span>
                                <span class="font-medium">{{ res.customer.full_name }}</span>
                                <span class="text-gray-600">{{ res.vehicle }}</span>
                            </div>
                            <a href="{% url 'reservation_checkin' res.pk %}"
                               class="btn btn-sm btn-success">
                                Check In
                            </a>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-gray-500">No returns scheduled for today</p>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Right Sidebar -->
        <div class="space-y-6">
            <!-- Quick Actions -->
            <div class="bg-white rounded-lg shadow p-4">
                <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
                <div class="space-y-2">
                    <a href="{% url 'reservation_create' %}"
                       class="block w-full btn btn-primary text-center">
                        + New Reservation
                    </a>
                    <a href="{% url 'customer_create' %}"
                       class="block w-full btn btn-secondary text-center">
                        + Add Customer
                    </a>
                    <a href="{% url 'vehicle_create' %}"
                       class="block w-full btn btn-secondary text-center">
                        + Add Vehicle
                    </a>
                    <a href="{% url 'calendar' %}"
                       class="block w-full btn btn-secondary text-center">
                        View Calendar
                    </a>
                </div>
            </div>

            <!-- Alerts -->
            {% if alerts %}
            <div class="bg-white rounded-lg shadow p-4">
                <h2 class="text-lg font-semibold mb-4">Alerts</h2>
                <div class="space-y-2">
                    {% for alert in alerts %}
                    <a href="{{ alert.link }}"
                       class="block p-3 rounded {% if alert.type == 'danger' %}bg-red-50{% elif alert.type == 'warning' %}bg-yellow-50{% else %}bg-blue-50{% endif %}">
                        <span>{{ alert.icon }}</span>
                        <span class="ml-2">{{ alert.message }}</span>
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

### URL Configuration
```python
# apps/dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
]

# config/urls.py
urlpatterns = [
    path('', include('apps.dashboard.urls')),
    # ... other urls
]
```

## Definition of Done
- [ ] Dashboard app created
- [ ] Dashboard view with all context data
- [ ] Today's schedule displays correctly
- [ ] Statistics cards show accurate data
- [ ] Alerts system works
- [ ] Quick actions functional
- [ ] Tests written and passing (>95% coverage)
