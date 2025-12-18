"""
URL configuration for platform admin.
"""
from django.urls import path
from . import views

app_name = 'platform_admin'

urlpatterns = [
    # Dashboard
    path('', views.PlatformDashboardView.as_view(), name='dashboard'),

    # Tenant management
    path('tenants/', views.TenantListView.as_view(), name='tenant_list'),
    path('tenants/<int:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    path('tenants/<int:pk>/edit/', views.TenantEditView.as_view(), name='tenant_edit'),
    path('tenants/<int:pk>/suspend/', views.TenantSuspendView.as_view(), name='tenant_suspend'),

    # User impersonation
    path('impersonate/<int:user_id>/', views.ImpersonateStartView.as_view(), name='impersonate_start'),
    path('impersonate/end/', views.ImpersonateEndView.as_view(), name='impersonate_end'),

    # Platform settings
    path('settings/', views.PlatformSettingsView.as_view(), name='settings'),

    # Audit logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_logs'),
]
