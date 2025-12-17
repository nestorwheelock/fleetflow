from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from apps.tenants.mixins import TenantViewMixin
from .models import Contract, ConditionReport, ConditionReportPhoto
from .serializers import (
    ContractSerializer, ContractListSerializer,
    ConditionReportSerializer, ConditionReportPhotoSerializer,
    SignatureSerializer,
)


class ContractViewSet(TenantViewMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['contract_number', 'reservation__customer__first_name', 'reservation__customer__last_name']
    ordering_fields = ['created_at', 'contract_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContractListSerializer
        return ContractSerializer

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return Contract.objects.none()
        return Contract.objects.filter(
            tenant=tenant
        ).select_related('reservation', 'reservation__customer', 'reservation__vehicle')

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        contract = self.get_object()
        pdf_content = contract.generate_pdf()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{contract.contract_number}.pdf"'
        return response

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        contract = self.get_object()
        pdf_content = contract.generate_pdf()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{contract.contract_number}.pdf"'
        return response

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        contract = self.get_object()
        serializer = SignatureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signature = serializer.validated_data['signature']
        is_customer = serializer.validated_data.get('is_customer', True)

        contract.sign(signature, is_customer=is_customer)

        return Response({
            'status': 'signed',
            'signed_at': contract.customer_signed_at if is_customer else contract.staff_signed_at
        })

    @action(detail=True, methods=['post'], url_path='condition-report')
    def condition_report(self, request, pk=None):
        contract = self.get_object()
        serializer = ConditionReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='condition-reports')
    def get_condition_reports(self, request, pk=None):
        contract = self.get_object()
        reports = contract.condition_reports.all()
        serializer = ConditionReportSerializer(reports, many=True)
        return Response(serializer.data)


class ConditionReportViewSet(TenantViewMixin, viewsets.ModelViewSet):
    serializer_class = ConditionReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return ConditionReport.objects.none()
        return ConditionReport.objects.filter(
            contract__tenant=tenant
        ).select_related('contract')

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        report = self.get_object()
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        location = request.data.get('location', 'other')
        description = request.data.get('description', '')

        photo = ConditionReportPhoto.objects.create(
            condition_report=report,
            image=image,
            location=location,
            description=description
        )
        serializer = ConditionReportPhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
