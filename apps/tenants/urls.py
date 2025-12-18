from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, TenantUserViewSet, TenantSettingsView, TestAPIKeyView

router = DefaultRouter()
router.register(r'users', TenantUserViewSet, basename='tenant-user')
router.register(r'', TenantViewSet, basename='tenant')

urlpatterns = [
    path('settings/', TenantSettingsView.as_view(), name='tenant-settings'),
    path('settings/test-api-key/', TestAPIKeyView.as_view(), name='test-api-key'),
    path('', include(router.urls)),
]
