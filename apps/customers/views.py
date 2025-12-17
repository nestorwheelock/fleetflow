from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from apps.tenants.mixins import TenantViewMixin
from .models import Customer, CustomerDocument
from .serializers import CustomerSerializer, CustomerListSerializer, CustomerDocumentSerializer


class CustomerViewSet(TenantViewMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_blacklisted']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'license_number']
    ordering_fields = ['last_name', 'first_name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return Customer.objects.none()
        return Customer.objects.filter(tenant=tenant).prefetch_related('documents')

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)

    @action(detail=True, methods=['get'])
    def rentals(self, request, pk=None):
        customer = self.get_object()
        from apps.reservations.serializers import ReservationListSerializer
        rentals = customer.get_rental_history()
        serializer = ReservationListSerializer(rentals, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def blacklist(self, request, pk=None):
        customer = self.get_object()
        reason = request.data.get('reason', '')
        customer.is_blacklisted = True
        customer.blacklist_reason = reason
        customer.save(update_fields=['is_blacklisted', 'blacklist_reason', 'updated_at'])
        return Response({'status': 'blacklisted'})

    @action(detail=True, methods=['post'])
    def unblacklist(self, request, pk=None):
        customer = self.get_object()
        customer.is_blacklisted = False
        customer.blacklist_reason = ''
        customer.save(update_fields=['is_blacklisted', 'blacklist_reason', 'updated_at'])
        return Response({'status': 'unblacklisted'})

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_document(self, request, pk=None):
        customer = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document_type = request.data.get('document_type', 'other')
        description = request.data.get('description', '')

        tenant = self.get_tenant()
        document = CustomerDocument.objects.create(
            tenant=tenant,
            customer=customer,
            file=file,
            document_type=document_type,
            description=description
        )
        serializer = CustomerDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='documents/(?P<doc_id>[^/.]+)')
    def delete_document(self, request, pk=None, doc_id=None):
        customer = self.get_object()
        try:
            document = CustomerDocument.objects.get(pk=doc_id, customer=customer)
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CustomerDocument.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
