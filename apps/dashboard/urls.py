from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard-home'),

    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle-edit'),

    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),

    path('reservations/', views.ReservationListView.as_view(), name='reservation-list'),
    path('reservations/calendar/', views.reservation_calendar, name='reservation-calendar'),
    path('reservations/<int:pk>/', views.ReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/checkout/', views.reservation_checkout, name='reservation-checkout'),
    path('reservations/<int:pk>/checkin/', views.reservation_checkin, name='reservation-checkin'),

    path('contracts/', views.ContractListView.as_view(), name='contract-list'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
    path('contracts/<int:pk>/pdf/', views.contract_pdf, name='contract-pdf'),

    path('api/dashboard/stats/', views.DashboardStatsAPI.as_view(), name='api-dashboard-stats'),
    path('api/dashboard/today/', views.DashboardTodayAPI.as_view(), name='api-dashboard-today'),
    path('api/dashboard/revenue/', views.DashboardRevenueAPI.as_view(), name='api-dashboard-revenue'),
    path('api/dashboard/fleet-status/', views.DashboardFleetStatusAPI.as_view(), name='api-dashboard-fleet-status'),
    path('api/dashboard/upcoming/', views.DashboardUpcomingAPI.as_view(), name='api-dashboard-upcoming'),
    path('api/dashboard/quick-actions/new-reservation/', views.QuickActionNewReservationAPI.as_view(), name='api-quick-action-new-reservation'),
    path('api/dashboard/quick-actions/new-customer/', views.QuickActionNewCustomerAPI.as_view(), name='api-quick-action-new-customer'),
    path('api/dashboard/quick-actions/vehicle-status/', views.QuickActionVehicleStatusAPI.as_view(), name='api-quick-action-vehicle-status'),
]
