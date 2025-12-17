from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from apps.tenants.mixins import TenantViewMixin
from .models import Vehicle, VehicleCategory, VehiclePhoto
from .serializers import (
    VehicleSerializer, VehicleListSerializer,
    VehicleCategorySerializer, VehiclePhotoSerializer
)


class VehicleCategoryViewSet(TenantViewMixin, viewsets.ModelViewSet):
    serializer_class = VehicleCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return VehicleCategory.objects.none()
        return VehicleCategory.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)


class VehicleViewSet(TenantViewMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'make', 'transmission', 'fuel_type']
    search_fields = ['make', 'model', 'license_plate', 'vin']
    ordering_fields = ['make', 'model', 'year', 'daily_rate', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleListSerializer
        return VehicleSerializer

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return Vehicle.objects.none()
        return Vehicle.objects.filter(tenant=tenant).select_related('category').prefetch_related('photos')

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        if not tenant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No tenant associated with user.')
        if not tenant.can_add_vehicle():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Vehicle limit reached for your plan.')
        serializer.save(tenant=tenant)

    @action(detail=False, methods=['get'])
    def available(self, request):
        vehicles = self.get_queryset().filter(status='available')
        serializer = VehicleListSerializer(vehicles, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        vehicle = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Vehicle.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        vehicle.status = new_status
        vehicle.save(update_fields=['status', 'updated_at'])
        return Response({'status': vehicle.status})

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        vehicle = self.get_object()
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_primary = request.data.get('is_primary', 'false').lower() == 'true'
        caption = request.data.get('caption', '')

        photo = VehiclePhoto.objects.create(
            vehicle=vehicle,
            image=image,
            is_primary=is_primary,
            caption=caption
        )
        serializer = VehiclePhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)')
    def delete_photo(self, request, pk=None, photo_id=None):
        vehicle = self.get_object()
        try:
            photo = VehiclePhoto.objects.get(pk=photo_id, vehicle=vehicle)
            photo.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VehiclePhoto.DoesNotExist:
            return Response(
                {'error': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )
