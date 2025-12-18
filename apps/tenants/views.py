import httpx
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Tenant, TenantUser, TenantSettings
from .serializers import (
    TenantSerializer, TenantUserSerializer, TenantStatsSerializer,
    TenantSettingsSerializer
)
from .mixins import TenantViewMixin


class TenantViewSet(TenantViewMixin, viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return Tenant.objects.none()
        return Tenant.objects.filter(pk=tenant.pk)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        tenant = self.get_object()

        from apps.fleet.models import Vehicle
        from apps.customers.models import Customer
        from apps.reservations.models import Reservation

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        vehicle_count = Vehicle.objects.filter(tenant=tenant).count()
        customer_count = Customer.objects.filter(tenant=tenant).count()
        reservation_count = Reservation.objects.filter(tenant=tenant).count()
        active_rentals = Reservation.objects.filter(
            tenant=tenant,
            status='checked_out'
        ).count()

        revenue = Reservation.objects.filter(
            tenant=tenant,
            status__in=['completed', 'checked_out'],
            start_date__gte=month_start.date()
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        data = {
            'vehicle_count': vehicle_count,
            'customer_count': customer_count,
            'reservation_count': reservation_count,
            'active_rentals': active_rentals,
            'revenue_this_month': revenue,
        }

        return Response(data)

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        tenant = self.get_object()
        users = TenantUser.objects.filter(tenant=tenant)
        serializer = TenantUserSerializer(users, many=True)
        return Response(serializer.data)


class TenantUserViewSet(TenantViewMixin, viewsets.ModelViewSet):
    serializer_class = TenantUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return TenantUser.objects.none()
        return TenantUser.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)


class TenantSettingsView(TenantViewMixin, APIView):
    """API endpoint for managing tenant automation settings."""
    permission_classes = [IsAuthenticated]

    def get_settings(self, tenant):
        """Get or create tenant settings."""
        settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
        return settings

    def get(self, request):
        """Get current tenant settings."""
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        settings = self.get_settings(tenant)
        serializer = TenantSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        """Update tenant settings."""
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        tenant_user = self.get_tenant_user()
        if not tenant_user or tenant_user.role != 'owner':
            return Response(
                {'error': 'Only tenant owners can modify settings'},
                status=status.HTTP_403_FORBIDDEN
            )

        settings = self.get_settings(tenant)
        serializer = TenantSettingsSerializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestAPIKeyView(TenantViewMixin, APIView):
    """API endpoint to test OpenRouter API key validity."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Test if the provided or stored API key is valid."""
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        api_key = request.data.get('api_key')

        if not api_key:
            settings, _ = TenantSettings.objects.get_or_create(tenant=tenant)
            api_key = settings.get_api_key()

        if not api_key:
            return Response(
                {'valid': False, 'error': 'No API key provided or stored'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    'https://openrouter.ai/api/v1/auth/key',
                    headers={'Authorization': f'Bearer {api_key}'}
                )

            if response.status_code == 200:
                data = response.json().get('data', {})
                return Response({
                    'valid': True,
                    'message': 'API key is valid',
                    'label': data.get('label', ''),
                    'limit': data.get('limit'),
                    'usage': data.get('usage'),
                })
            elif response.status_code == 401:
                return Response({
                    'valid': False,
                    'error': 'Invalid API key - authentication failed'
                })
            else:
                return Response({
                    'valid': False,
                    'error': f'API error: {response.status_code}'
                })
        except httpx.TimeoutException:
            return Response({
                'valid': False,
                'error': 'Connection timeout - please try again'
            })
        except Exception as e:
            return Response({
                'valid': False,
                'error': f'Connection error: {str(e)}'
            })
