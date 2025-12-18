import pytest
import io
from unittest.mock import patch, MagicMock
from datetime import date
from django.urls import reverse
from rest_framework.test import APIClient

from apps.automation.ocr.utils.encryption import reset_encryption_key_cache
from apps.automation.ocr.schemas.license import LicenseOCRResponse, LicenseAddress
from apps.automation.ocr.schemas.insurance import InsuranceOCRResponse


@pytest.fixture(autouse=True)
def reset_encryption_cache():
    reset_encryption_key_cache()
    yield
    reset_encryption_key_cache()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user, tenant, tenant_user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def professional_tenant(tenant, settings):
    settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
    reset_encryption_key_cache()
    from apps.tenants.models import TenantSettings
    tenant.plan = 'professional'
    tenant.save()
    tenant_settings = TenantSettings.objects.create(
        tenant=tenant,
        openrouter_enabled=True,
        openrouter_model='anthropic/claude-3.5-sonnet',
        auto_parse_license=True,
        auto_parse_insurance=True,
    )
    tenant_settings.set_api_key('sk-or-test-api-key')
    tenant_settings.save()
    return tenant


@pytest.fixture
def starter_tenant(tenant, settings):
    settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
    reset_encryption_key_cache()
    tenant.plan = 'starter'
    tenant.save()
    return tenant


@pytest.fixture
def mock_license_result():
    return LicenseOCRResponse(
        country='USA',
        issuing_authority='California',
        license_number='D1234567',
        license_class='C',
        issue_date=date(2020, 5, 15),
        expiration_date=date(2028, 5, 15),
        first_name='John',
        middle_name='Robert',
        last_name='Smith',
        date_of_birth=date(1985, 3, 20),
        address=LicenseAddress(
            street='123 Main St',
            city='Los Angeles',
            state='CA',
            zip_code='90001'
        ),
        gender='M',
        height="5'10\"",
        weight='180 lbs',
        eye_color='BRN',
        hair_color='BLK',
        restrictions='B',
        endorsements='M',
        donor_status=True,
        confidence=0.95,
        has_photo=True
    )


@pytest.fixture
def mock_insurance_result():
    return InsuranceOCRResponse(
        company_name='State Farm',
        policy_number='SF-123456789',
        group_number='GRP001',
        effective_date=date(2024, 1, 1),
        expiration_date=date(2025, 1, 1),
        policyholder_name='John Smith',
        policyholder_relationship='Self',
        coverage_type='Full Coverage',
        covered_vehicles=[],
        agent_name='Jane Agent',
        agent_phone='555-123-4567',
        confidence=0.92
    )


@pytest.fixture
def test_image():
    image = io.BytesIO()
    image.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    image.seek(0)
    image.name = 'test_license.png'
    return image


@pytest.mark.django_db
class TestParseLicenseView:
    def test_parse_license_requires_authentication(self, api_client):
        url = reverse('automation:parse-license')
        response = api_client.post(url)
        assert response.status_code in [401, 403]

    def test_parse_license_requires_professional_plan(
        self, authenticated_client, starter_tenant, test_image
    ):
        url = reverse('automation:parse-license')
        response = authenticated_client.post(url, {'image': test_image}, format='multipart')
        assert response.status_code == 403
        assert 'plan does not include' in response.data['error']

    def test_parse_license_requires_image(
        self, authenticated_client, professional_tenant
    ):
        url = reverse('automation:parse-license')
        response = authenticated_client.post(url, {}, format='multipart')
        assert response.status_code == 400
        assert 'No image provided' in response.data['error']

    def test_parse_license_success(
        self, authenticated_client, professional_tenant,
        test_image, mock_license_result
    ):
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_license_result

        with patch('apps.automation.ocr.parsers.LicenseParser') as mock_parser_class:
            mock_parser_class.return_value = mock_parser
            url = reverse('automation:parse-license')
            response = authenticated_client.post(url, {'image': test_image}, format='multipart')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['first_name'] == 'John'
        assert response.data['data']['last_name'] == 'Smith'
        assert response.data['data']['license_number'] == 'D1234567'
        assert response.data['data']['confidence'] == 0.95

    def test_parse_license_with_customer_id(
        self, authenticated_client, professional_tenant,
        customer, test_image, mock_license_result
    ):
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_license_result

        with patch('apps.automation.ocr.parsers.LicenseParser') as mock_parser_class:
            mock_parser_class.return_value = mock_parser
            url = reverse('automation:parse-license-customer', args=[customer.id])
            response = authenticated_client.post(url, {'image': test_image}, format='multipart')

        assert response.status_code == 200
        assert response.data['customer_id'] == customer.id

    def test_parse_license_ocr_failure(
        self, authenticated_client, professional_tenant, test_image
    ):
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception('OCR service error')

        with patch('apps.automation.ocr.parsers.LicenseParser') as mock_parser_class:
            mock_parser_class.return_value = mock_parser
            url = reverse('automation:parse-license')
            response = authenticated_client.post(url, {'image': test_image}, format='multipart')

        assert response.status_code == 500
        assert 'OCR processing failed' in response.data['error']

    def test_parse_license_rate_limited(
        self, authenticated_client, professional_tenant, test_image
    ):
        from apps.tenants.models import TenantSettings
        settings = TenantSettings.objects.get(tenant=professional_tenant)
        settings.ocr_requests_today = 100
        settings.ocr_requests_reset_at = date.today()
        settings.save()

        url = reverse('automation:parse-license')
        response = authenticated_client.post(url, {'image': test_image}, format='multipart')

        assert response.status_code == 429
        assert 'limit reached' in response.data['error']


@pytest.mark.django_db
class TestParseInsuranceView:
    def test_parse_insurance_requires_authentication(self, api_client):
        url = reverse('automation:parse-insurance')
        response = api_client.post(url)
        assert response.status_code in [401, 403]

    def test_parse_insurance_requires_professional_plan(
        self, authenticated_client, starter_tenant, test_image
    ):
        url = reverse('automation:parse-insurance')
        response = authenticated_client.post(url, {'image': test_image}, format='multipart')
        assert response.status_code == 403
        assert 'plan does not include' in response.data['error']

    def test_parse_insurance_requires_image(
        self, authenticated_client, professional_tenant
    ):
        url = reverse('automation:parse-insurance')
        response = authenticated_client.post(url, {}, format='multipart')
        assert response.status_code == 400
        assert 'No image provided' in response.data['error']

    def test_parse_insurance_success(
        self, authenticated_client, professional_tenant,
        test_image, mock_insurance_result
    ):
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_insurance_result

        with patch('apps.automation.ocr.parsers.InsuranceParser') as mock_parser_class:
            mock_parser_class.return_value = mock_parser
            url = reverse('automation:parse-insurance')
            response = authenticated_client.post(url, {'image': test_image}, format='multipart')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['company_name'] == 'State Farm'
        assert response.data['data']['policy_number'] == 'SF-123456789'
        assert response.data['data']['confidence'] == 0.92


@pytest.mark.django_db
class TestApplyLicenseDataView:
    def test_apply_license_requires_authentication(self, api_client, customer):
        url = reverse('automation:apply-license', args=[customer.id])
        response = api_client.post(url)
        assert response.status_code in [401, 403]

    def test_apply_license_data_success(
        self, authenticated_client, professional_tenant, customer
    ):
        customer.license_number = ''
        customer.city = ''
        customer.gender = ''
        customer.eye_color = ''
        customer.save()

        url = reverse('automation:apply-license', args=[customer.id])
        data = {
            'fields': ['license_number', 'address_city', 'gender', 'eye_color'],
            'data': {
                'license_number': 'D1234567',
                'address_city': 'Los Angeles',
                'gender': 'M',
                'eye_color': 'BRN',
                'confidence': 0.95
            }
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'license_number' in response.data['applied_fields']
        assert 'address_city' in response.data['applied_fields']
        assert 'gender' in response.data['applied_fields']
        assert 'eye_color' in response.data['applied_fields']

        customer.refresh_from_db()
        assert customer.license_number == 'D1234567'
        assert customer.city == 'Los Angeles'
        assert customer.gender == 'M'
        assert customer.eye_color == 'BRN'
        assert customer.license_ocr_confidence == 0.95

    def test_apply_license_skips_existing_values(
        self, authenticated_client, professional_tenant, customer
    ):
        customer.gender = ''
        customer.save()

        url = reverse('automation:apply-license', args=[customer.id])
        data = {
            'fields': ['first_name', 'last_name', 'gender'],
            'data': {
                'first_name': 'John',
                'last_name': 'Smith',
                'gender': 'M'
            }
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 200
        assert 'first_name' in response.data['skipped_fields']
        assert 'last_name' in response.data['skipped_fields']
        assert 'gender' in response.data['applied_fields']

        customer.refresh_from_db()
        assert customer.first_name == 'John'
        assert customer.last_name == 'Doe'
        assert customer.gender == 'M'

    def test_apply_license_invalid_customer(
        self, authenticated_client, professional_tenant
    ):
        url = reverse('automation:apply-license', args=[99999])
        data = {
            'fields': ['first_name'],
            'data': {'first_name': 'John'}
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == 404

    def test_apply_license_empty_fields(
        self, authenticated_client, professional_tenant, customer
    ):
        url = reverse('automation:apply-license', args=[customer.id])
        data = {
            'fields': ['license_number'],
            'data': {'license_number': ''}
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 200
        assert 'license_number' in response.data['skipped_fields']


@pytest.mark.django_db
class TestApplyInsuranceDataView:
    def test_apply_insurance_requires_authentication(self, api_client, customer):
        url = reverse('automation:apply-insurance', args=[customer.id])
        response = api_client.post(url)
        assert response.status_code in [401, 403]

    def test_apply_insurance_data_success(
        self, authenticated_client, professional_tenant, customer
    ):
        url = reverse('automation:apply-insurance', args=[customer.id])
        data = {
            'data': {
                'company_name': 'State Farm',
                'policy_number': 'SF-123456789',
                'group_number': 'GRP001',
                'effective_date': '2024-01-01',
                'expiration_date': '2025-01-01',
                'policyholder_name': 'John Smith',
                'policyholder_relationship': 'Self',
                'coverage_type': 'Full Coverage',
                'covered_vehicles': [],
                'agent_name': 'Jane Agent',
                'agent_phone': '555-123-4567',
                'confidence': 0.92
            }
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'insurance_id' in response.data

        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.get(pk=response.data['insurance_id'])
        assert insurance.company_name == 'State Farm'
        assert insurance.policy_number == 'SF-123456789'
        assert insurance.customer == customer
        assert insurance.ocr_confidence == 0.92

    def test_apply_insurance_invalid_customer(
        self, authenticated_client, professional_tenant
    ):
        url = reverse('automation:apply-insurance', args=[99999])
        data = {
            'data': {
                'company_name': 'State Farm',
                'policy_number': 'SF-123'
            }
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == 404

    def test_apply_insurance_validation_error(
        self, authenticated_client, professional_tenant, customer
    ):
        url = reverse('automation:apply-insurance', args=[customer.id])
        data = {}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestOCRAccessMixin:
    def test_ocr_disabled_returns_error(
        self, authenticated_client, tenant, settings, test_image
    ):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()

        from apps.tenants.models import TenantSettings
        tenant.plan = 'professional'
        tenant.save()
        TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=False
        )

        url = reverse('automation:parse-license')
        response = authenticated_client.post(url, {'image': test_image}, format='multipart')
        assert response.status_code == 400
        assert 'not enabled' in response.data['error']

    def test_no_api_key_returns_error(
        self, authenticated_client, tenant, settings, test_image
    ):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()

        from apps.tenants.models import TenantSettings
        tenant.plan = 'professional'
        tenant.save()
        TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=True
        )

        url = reverse('automation:parse-license')
        response = authenticated_client.post(url, {'image': test_image}, format='multipart')
        assert response.status_code == 400
        assert 'No API key' in response.data['error']
