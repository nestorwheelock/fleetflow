from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import date, timedelta

from apps.tenants.mixins import TenantViewMixin
from apps.fleet.models import Vehicle
from .models import Reservation, ReservationExtra
from .serializers import (
    ReservationSerializer, ReservationListSerializer,
    ReservationExtraSerializer, CalendarEventSerializer,
)


class ReservationExtraViewSet(TenantViewMixin, viewsets.ModelViewSet):
    serializer_class = ReservationExtraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return ReservationExtra.objects.none()
        return ReservationExtra.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)


class ReservationViewSet(TenantViewMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'vehicle', 'customer']
    search_fields = ['customer__first_name', 'customer__last_name', 'vehicle__license_plate']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'total_amount']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservationListSerializer
        if self.action == 'calendar':
            return CalendarEventSerializer
        return ReservationSerializer

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return Reservation.objects.none()

        queryset = Reservation.objects.filter(
            tenant=tenant
        ).select_related('vehicle', 'customer')

        start_after = self.request.query_params.get('start_date_after')
        start_before = self.request.query_params.get('start_date_before')
        if start_after:
            queryset = queryset.filter(start_date__gte=start_after)
        if start_before:
            queryset = queryset.filter(start_date__lte=start_before)

        return queryset

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        reservation = self.get_object()
        mileage = request.data.get('mileage')
        try:
            reservation.checkout(mileage=mileage)
            return Response({'status': 'checked_out'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        reservation = self.get_object()
        mileage = request.data.get('mileage')
        try:
            reservation.checkin(mileage=mileage)
            return Response({'status': 'completed'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        try:
            reservation.cancel()
            return Response({'status': 'cancelled'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        start = request.query_params.get('start', date.today().isoformat())
        end = request.query_params.get('end', (date.today() + timedelta(days=30)).isoformat())

        reservations = self.get_queryset().filter(
            start_date__lte=end,
            end_date__gte=start,
        ).exclude(status__in=['cancelled', 'no_show'])

        serializer = CalendarEventSerializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='check-availability')
    def check_availability(self, request):
        vehicle_id = request.query_params.get('vehicle')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not all([vehicle_id, start_date, end_date]):
            return Response(
                {'error': 'vehicle, start_date, and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tenant = self.get_tenant()
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id, tenant=tenant)
        except Vehicle.DoesNotExist:
            return Response(
                {'error': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()

        available = Reservation.check_availability(vehicle, start, end)

        return Response({
            'vehicle': vehicle_id,
            'start_date': start_date,
            'end_date': end_date,
            'available': available,
        })

    @action(detail=False, methods=['get'])
    def today(self, request):
        today = date.today()

        checkouts = self.get_queryset().filter(
            start_date=today,
            status__in=['pending', 'confirmed']
        )

        checkins = self.get_queryset().filter(
            end_date=today,
            status='checked_out'
        )

        return Response({
            'checkouts': ReservationListSerializer(checkouts, many=True).data,
            'checkins': ReservationListSerializer(checkins, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        today = date.today()
        upcoming = self.get_queryset().filter(
            start_date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('start_date')[:10]

        return Response(ReservationListSerializer(upcoming, many=True).data)
