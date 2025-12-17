from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, ConditionReportViewSet

router = DefaultRouter()
router.register(r'condition-reports', ConditionReportViewSet, basename='condition-report')
router.register(r'', ContractViewSet, basename='contract')

urlpatterns = [
    path('', include(router.urls)),
]
