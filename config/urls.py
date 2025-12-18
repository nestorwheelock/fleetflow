from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.tenants.forms import EmailAuthenticationForm

urlpatterns = [
    # Authentication with email-based login
    path('login/', auth_views.LoginView.as_view(
        authentication_form=EmailAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Django admin (obscured URL, superuser only)
    path('django-admin/', admin.site.urls),

    # Platform admin (super admin dashboard)
    path('admin-platform/', include('apps.platform_admin.urls')),

    # API endpoints
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/fleet/', include('apps.fleet.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/reservations/', include('apps.reservations.urls')),
    path('api/contracts/', include('apps.contracts.urls')),
    path('api/automation/', include('apps.automation.urls')),

    # Dashboard
    path('dashboard/', include('apps.dashboard.urls')),

    # Public pages (tenant landing pages via subdomain)
    path('public/', include('apps.public.urls')),

    # Root URL handled by dashboard or public landing depending on context
    path('', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
