"""
URL configuration for public tenant pages.
"""
from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('vehicles/', views.VehicleGalleryView.as_view(), name='vehicles'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),

    # Customer portal
    path('register/', views.CustomerRegisterView.as_view(), name='customer_register'),
    path('customer/', views.CustomerPortalView.as_view(), name='customer_portal'),
    path('customer/documents/', views.CustomerDocumentUploadView.as_view(), name='customer_documents'),
    path('customer/reservations/', views.CustomerReservationsView.as_view(), name='customer_reservations'),
]
