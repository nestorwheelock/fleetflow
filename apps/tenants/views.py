from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Tenant, TenantUser
from .serializers import TenantSerializer, TenantUserSerializer, TenantStatsSerializer
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
