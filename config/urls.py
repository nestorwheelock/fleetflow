from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('admin/', admin.site.urls),
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/fleet/', include('apps.fleet.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/reservations/', include('apps.reservations.urls')),
    path('api/contracts/', include('apps.contracts.urls')),
    path('api/automation/', include('apps.automation.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
