from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.tenants.mixins import TenantViewMixin
from apps.tenants.models import TenantSettings
from apps.customers.models import Customer, CustomerInsurance
from apps.automation.integration.feature_check import check_ocr_access, tenant_has_feature
from .serializers import (
    LicenseDataSerializer,
    InsuranceDataSerializer,
    ApplyLicenseDataSerializer,
    ApplyInsuranceDataSerializer,
)


class OCRAccessMixin:
    """Mixin to check OCR access for a tenant."""

    def check_ocr_permission(self, tenant, feature='license_ocr'):
        """Check if tenant has OCR access.

        Returns tuple of (has_access, error_response or None)
        """
        if not tenant_has_feature(tenant, feature):
            return False, Response(
                {'error': f'Your plan does not include {feature.replace("_", " ")}. Please upgrade to Professional or higher.'},
                status=status.HTTP_403_FORBIDDEN
            )

        settings = getattr(tenant, 'settings', None)
        if not settings or not settings.openrouter_enabled:
            return False, Response(
                {'error': 'OCR is not enabled. Please configure your OpenRouter API key in settings.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not settings.has_api_key:
            return False, Response(
                {'error': 'No API key configured. Please add your OpenRouter API key in settings.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not settings.can_make_ocr_request():
            return False, Response(
                {'error': 'Daily OCR request limit reached. Please try again tomorrow.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        return True, None

    def get_parser_client(self, tenant):
        """Get a configured parser for the tenant."""
        settings = tenant.settings
        api_key = settings.get_api_key()
        model = settings.openrouter_model

        from apps.automation.ocr.client import OpenRouterClient
        return OpenRouterClient(api_key=api_key, model=model)


class ParseLicenseView(TenantViewMixin, OCRAccessMixin, APIView):
    """Parse a driver's license image using OCR."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, customer_id=None):
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        has_access, error_response = self.check_ocr_permission(tenant, 'license_ocr')
        if not has_access:
            return error_response

        image_file = request.FILES.get('image')
        if customer_id:
            customer = get_object_or_404(Customer, pk=customer_id, tenant=tenant)
            if not image_file and customer.license_image_front:
                image_file = customer.license_image_front

        if not image_file:
            return Response(
                {'error': 'No image provided. Please upload a license image.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_data = image_file.read()
            image_file.seek(0)

            content_type = getattr(image_file, 'content_type', 'image/jpeg')

            from apps.automation.ocr.parsers import LicenseParser
            client = self.get_parser_client(tenant)
            parser = LicenseParser(client)

            result = parser.parse(image_data, image_media_type=content_type)

            tenant.settings.increment_ocr_requests()

            response_data = {
                'success': True,
                'data': {
                    'country': result.country,
                    'issuing_authority': result.issuing_authority,
                    'license_number': result.license_number,
                    'license_class': result.license_class,
                    'issue_date': result.issue_date.isoformat() if result.issue_date else None,
                    'expiration_date': result.expiration_date.isoformat() if result.expiration_date else None,
                    'first_name': result.first_name,
                    'middle_name': result.middle_name,
                    'last_name': result.last_name,
                    'date_of_birth': result.date_of_birth.isoformat() if result.date_of_birth else None,
                    'address_street': result.address.street,
                    'address_city': result.address.city,
                    'address_state': result.address.state,
                    'address_zip': result.address.zip_code,
                    'gender': result.gender,
                    'height': result.height,
                    'weight': result.weight,
                    'eye_color': result.eye_color,
                    'hair_color': result.hair_color,
                    'restrictions': result.restrictions,
                    'endorsements': result.endorsements,
                    'donor_status': result.donor_status,
                    'confidence': result.confidence,
                    'has_photo': result.has_photo,
                },
                'customer_id': customer_id,
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {'error': f'OCR processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ParseInsuranceView(TenantViewMixin, OCRAccessMixin, APIView):
    """Parse an insurance card image using OCR."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, customer_id=None):
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        has_access, error_response = self.check_ocr_permission(tenant, 'insurance_ocr')
        if not has_access:
            return error_response

        image_file = request.FILES.get('image')

        if not image_file:
            return Response(
                {'error': 'No image provided. Please upload an insurance card image.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_data = image_file.read()
            image_file.seek(0)

            content_type = getattr(image_file, 'content_type', 'image/jpeg')

            from apps.automation.ocr.parsers import InsuranceParser
            client = self.get_parser_client(tenant)
            parser = InsuranceParser(client)

            result = parser.parse(image_data, image_media_type=content_type)

            tenant.settings.increment_ocr_requests()

            response_data = {
                'success': True,
                'data': {
                    'company_name': result.company_name,
                    'policy_number': result.policy_number,
                    'group_number': result.group_number,
                    'effective_date': result.effective_date.isoformat() if result.effective_date else None,
                    'expiration_date': result.expiration_date.isoformat() if result.expiration_date else None,
                    'policyholder_name': result.policyholder_name,
                    'policyholder_relationship': result.policyholder_relationship,
                    'coverage_type': result.coverage_type,
                    'covered_vehicles': [
                        {
                            'year': v.year,
                            'make': v.make,
                            'model': v.model,
                            'vin': v.vin
                        } for v in result.covered_vehicles
                    ],
                    'agent_name': result.agent_name,
                    'agent_phone': result.agent_phone,
                    'confidence': result.confidence,
                },
                'customer_id': customer_id,
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {'error': f'OCR processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ApplyLicenseDataView(TenantViewMixin, APIView):
    """Apply parsed license data to a customer record."""
    permission_classes = [IsAuthenticated]

    FIELD_MAPPING = {
        'first_name': 'first_name',
        'middle_name': 'middle_name',
        'last_name': 'last_name',
        'date_of_birth': 'date_of_birth',
        'license_number': 'license_number',
        'license_class': 'license_class',
        'issuing_authority': 'license_state',
        'issue_date': 'license_issue_date',
        'expiration_date': 'license_expiry',
        'restrictions': 'license_restrictions',
        'endorsements': 'license_endorsements',
        'donor_status': 'license_donor_status',
        'address_street': 'address',
        'address_city': 'city',
        'address_state': 'state',
        'address_zip': 'zip_code',
        'gender': 'gender',
        'height': 'height',
        'weight': 'weight',
        'eye_color': 'eye_color',
        'hair_color': 'hair_color',
    }

    def post(self, request, customer_id):
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        customer = get_object_or_404(Customer, pk=customer_id, tenant=tenant)

        serializer = ApplyLicenseDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fields_to_apply = serializer.validated_data['fields']
        data = serializer.validated_data['data']

        applied_fields = []
        skipped_fields = []

        for field in fields_to_apply:
            if field not in self.FIELD_MAPPING:
                continue

            customer_field = self.FIELD_MAPPING[field]
            value = data.get(field)

            if value is None or value == '':
                skipped_fields.append(field)
                continue

            current_value = getattr(customer, customer_field, None)
            if current_value and current_value != '':
                skipped_fields.append(field)
                continue

            setattr(customer, customer_field, value)
            applied_fields.append(field)

        if 'confidence' in data:
            customer.license_ocr_confidence = data['confidence']
        customer.license_ocr_parsed_at = timezone.now()
        customer.save()

        return Response({
            'success': True,
            'applied_fields': applied_fields,
            'skipped_fields': skipped_fields,
            'customer_id': customer_id,
        })


class ApplyInsuranceDataView(TenantViewMixin, APIView):
    """Apply parsed insurance data to create/update an insurance record."""
    permission_classes = [IsAuthenticated]

    def post(self, request, customer_id):
        tenant = self.get_tenant()
        if not tenant:
            return Response(
                {'error': 'No tenant found'},
                status=status.HTTP_404_NOT_FOUND
            )

        customer = get_object_or_404(Customer, pk=customer_id, tenant=tenant)

        serializer = ApplyInsuranceDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data['data']

        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name=data.get('company_name', ''),
            policy_number=data.get('policy_number', ''),
            group_number=data.get('group_number', ''),
            effective_date=data.get('effective_date'),
            expiration_date=data.get('expiration_date'),
            policyholder_name=data.get('policyholder_name', ''),
            policyholder_relationship=data.get('policyholder_relationship', ''),
            coverage_type=data.get('coverage_type', ''),
            covered_vehicles=data.get('covered_vehicles', []),
            agent_name=data.get('agent_name', ''),
            agent_phone=data.get('agent_phone', ''),
            ocr_parsed_at=timezone.now(),
            ocr_confidence=data.get('confidence', 0.0),
            is_active=True,
        )

        return Response({
            'success': True,
            'insurance_id': insurance.id,
            'customer_id': customer_id,
        })
