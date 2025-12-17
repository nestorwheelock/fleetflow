from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, VehicleCategoryViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'categories', VehicleCategoryViewSet, basename='vehicle-category')

urlpatterns = [
    path('', include(router.urls)),
]
