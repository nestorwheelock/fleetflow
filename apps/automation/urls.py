from django.urls import path
from .views import (
    ParseLicenseView,
    ParseInsuranceView,
    ApplyLicenseDataView,
    ApplyInsuranceDataView,
)

app_name = 'automation'

urlpatterns = [
    path('parse-license/', ParseLicenseView.as_view(), name='parse-license'),
    path('parse-license/<int:customer_id>/', ParseLicenseView.as_view(), name='parse-license-customer'),
    path('parse-insurance/', ParseInsuranceView.as_view(), name='parse-insurance'),
    path('parse-insurance/<int:customer_id>/', ParseInsuranceView.as_view(), name='parse-insurance-customer'),
    path('apply-license/<int:customer_id>/', ApplyLicenseDataView.as_view(), name='apply-license'),
    path('apply-insurance/<int:customer_id>/', ApplyInsuranceDataView.as_view(), name='apply-insurance'),
]
