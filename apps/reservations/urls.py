from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet, ReservationExtraViewSet

router = DefaultRouter()
router.register(r'extras', ReservationExtraViewSet, basename='reservation-extra')
router.register(r'', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]
