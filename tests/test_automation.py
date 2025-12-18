import pytest
from datetime import date, timedelta
from django.utils import timezone

from apps.automation.ocr.utils.encryption import (
    encrypt_api_key, decrypt_api_key, reset_encryption_key_cache
)
from apps.automation.integration.feature_check import tenant_has_feature, check_ocr_access


@pytest.fixture(autouse=True)
def reset_encryption_cache():
    """Reset the encryption key cache before each test."""
    reset_encryption_key_cache()
    yield
    reset_encryption_key_cache()


@pytest.mark.django_db
class TestEncryptionUtils:
    def test_encrypt_and_decrypt_api_key(self, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        api_key = 'sk-or-v1-test-api-key-12345'
        encrypted = encrypt_api_key(api_key)
        assert encrypted is not None
        assert encrypted != api_key.encode()
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == api_key

    def test_encrypt_empty_key_returns_none(self, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        assert encrypt_api_key('') is None
        assert encrypt_api_key(None) is None

    def test_decrypt_empty_key_returns_none(self, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        assert decrypt_api_key(None) is None
        assert decrypt_api_key(b'') is None

    def test_decrypt_invalid_data_returns_none(self, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        assert decrypt_api_key(b'invalid-encrypted-data') is None


@pytest.mark.django_db
class TestFeatureCheck:
    def test_starter_plan_no_ocr_features(self, tenant):
        tenant.plan = 'starter'
        tenant.save()
        assert not tenant_has_feature(tenant, 'license_ocr')
        assert not tenant_has_feature(tenant, 'insurance_ocr')

    def test_professional_plan_has_ocr_features(self, tenant):
        tenant.plan = 'professional'
        tenant.save()
        assert tenant_has_feature(tenant, 'license_ocr')
        assert tenant_has_feature(tenant, 'insurance_ocr')

    def test_business_plan_has_ocr_features(self, tenant):
        tenant.plan = 'business'
        tenant.save()
        assert tenant_has_feature(tenant, 'license_ocr')
        assert tenant_has_feature(tenant, 'insurance_ocr')

    def test_enterprise_plan_has_ocr_features(self, tenant):
        tenant.plan = 'enterprise'
        tenant.save()
        assert tenant_has_feature(tenant, 'license_ocr')
        assert tenant_has_feature(tenant, 'insurance_ocr')

    def test_check_ocr_access_denied_without_api_key(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant.plan = 'professional'
        tenant.save()
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=True
        )
        assert not check_ocr_access(tenant)

    def test_check_ocr_access_denied_when_disabled(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant.plan = 'professional'
        tenant.save()
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=False
        )
        tenant_settings.set_api_key('sk-or-test-key')
        tenant_settings.save()
        assert not check_ocr_access(tenant)

    def test_check_ocr_access_granted_with_config(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant.plan = 'professional'
        tenant.save()
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=True
        )
        tenant_settings.set_api_key('sk-or-test-key')
        tenant_settings.save()
        tenant.refresh_from_db()
        assert check_ocr_access(tenant)


@pytest.mark.django_db
class TestTenantSettings:
    def test_tenant_settings_creation(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=True,
            openrouter_model='anthropic/claude-3.5-sonnet',
            auto_parse_license=True,
            auto_parse_insurance=True
        )
        assert tenant_settings.tenant == tenant
        assert tenant_settings.openrouter_enabled is True
        assert tenant_settings.auto_parse_license is True
        assert tenant_settings.auto_parse_insurance is True

    def test_tenant_settings_str_representation(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(tenant=tenant)
        assert str(tenant_settings) == f'Settings for {tenant.name}'

    def test_has_api_key_property(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(tenant=tenant)
        assert tenant_settings.has_api_key is False
        tenant_settings.set_api_key('sk-or-test-key')
        tenant_settings.save()
        assert tenant_settings.has_api_key is True

    def test_api_key_encryption_decryption(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(tenant=tenant)
        api_key = 'sk-or-v1-secret-api-key-12345'
        tenant_settings.set_api_key(api_key)
        tenant_settings.save()
        retrieved = TenantSettings.objects.get(pk=tenant_settings.pk)
        assert retrieved.get_api_key() == api_key

    def test_rate_limiting_counter_reset(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            ocr_requests_today=50,
            ocr_requests_reset_at=date.today() - timedelta(days=1)
        )
        assert tenant_settings.can_make_ocr_request()
        tenant_settings.refresh_from_db()
        assert tenant_settings.ocr_requests_today == 0
        assert tenant_settings.ocr_requests_reset_at == date.today()

    def test_rate_limiting_at_limit(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            ocr_requests_today=100,
            ocr_requests_reset_at=date.today()
        )
        assert not tenant_settings.can_make_ocr_request()

    def test_increment_ocr_requests(self, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-encryption-key-secret'
        reset_encryption_key_cache()
        from apps.tenants.models import TenantSettings
        tenant_settings = TenantSettings.objects.create(
            tenant=tenant,
            ocr_requests_today=0,
            ocr_requests_reset_at=date.today()
        )
        tenant_settings.increment_ocr_requests()
        tenant_settings.refresh_from_db()
        assert tenant_settings.ocr_requests_today == 1


@pytest.mark.django_db
class TestCustomerOCRFields:
    def test_customer_profile_photo_fields(self, customer):
        assert hasattr(customer, 'profile_photo')
        assert hasattr(customer, 'profile_photo_source')

    def test_customer_middle_name_field(self, customer):
        customer.middle_name = 'Robert'
        customer.save()
        customer.refresh_from_db()
        assert customer.middle_name == 'Robert'

    def test_customer_extended_license_fields(self, customer):
        from datetime import date
        customer.license_issue_date = date(2020, 1, 15)
        customer.license_class = 'C'
        customer.license_restrictions = 'Corrective Lenses'
        customer.license_endorsements = 'Motorcycle'
        customer.license_donor_status = True
        customer.save()
        customer.refresh_from_db()
        assert customer.license_issue_date == date(2020, 1, 15)
        assert customer.license_class == 'C'
        assert customer.license_restrictions == 'Corrective Lenses'
        assert customer.license_endorsements == 'Motorcycle'
        assert customer.license_donor_status is True

    def test_customer_physical_characteristics(self, customer):
        customer.gender = 'Male'
        customer.height = "5'10\""
        customer.weight = '180 lbs'
        customer.eye_color = 'Brown'
        customer.hair_color = 'Black'
        customer.save()
        customer.refresh_from_db()
        assert customer.gender == 'Male'
        assert customer.height == "5'10\""
        assert customer.weight == '180 lbs'
        assert customer.eye_color == 'Brown'
        assert customer.hair_color == 'Black'

    def test_customer_ocr_metadata(self, customer):
        customer.license_ocr_parsed_at = timezone.now()
        customer.license_ocr_confidence = 0.95
        customer.save()
        customer.refresh_from_db()
        assert customer.license_ocr_parsed_at is not None
        assert customer.license_ocr_confidence == 0.95


@pytest.mark.django_db
class TestCustomerInsurance:
    def test_insurance_creation(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='State Farm',
            policy_number='SF123456789',
            group_number='GRP001',
            effective_date=date.today() - timedelta(days=30),
            expiration_date=date.today() + timedelta(days=335),
            policyholder_name='John Doe',
            coverage_type='full',
            is_active=True
        )
        assert insurance.company_name == 'State Farm'
        assert insurance.policy_number == 'SF123456789'
        assert insurance.is_active is True

    def test_insurance_str_representation(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Geico',
            policy_number='G987654321'
        )
        assert str(insurance) == f'{customer} - Geico (G987654321)'

    def test_insurance_is_expired(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Progressive',
            policy_number='P111222333',
            expiration_date=date.today() - timedelta(days=1)
        )
        assert insurance.is_expired() is True

    def test_insurance_is_not_expired(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Allstate',
            policy_number='A444555666',
            expiration_date=date.today() + timedelta(days=30)
        )
        assert insurance.is_expired() is False

    def test_insurance_is_valid(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Liberty Mutual',
            policy_number='LM777888999',
            effective_date=date.today() - timedelta(days=30),
            expiration_date=date.today() + timedelta(days=30)
        )
        assert insurance.is_valid() is True

    def test_insurance_is_invalid_before_effective(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Farmers',
            policy_number='F000111222',
            effective_date=date.today() + timedelta(days=10),
            expiration_date=date.today() + timedelta(days=365)
        )
        assert insurance.is_valid() is False

    def test_insurance_covered_vehicles_json(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        vehicles = [
            {'year': 2023, 'make': 'Toyota', 'model': 'Camry', 'vin': '1HGBH41JXMN109186'},
            {'year': 2022, 'make': 'Honda', 'model': 'Accord', 'vin': '2HGBH41JXMN109187'}
        ]
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='USAA',
            policy_number='U333444555',
            covered_vehicles=vehicles
        )
        insurance.refresh_from_db()
        assert len(insurance.covered_vehicles) == 2
        assert insurance.covered_vehicles[0]['make'] == 'Toyota'

    def test_insurance_ocr_metadata(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        insurance = CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Nationwide',
            policy_number='N666777888',
            ocr_parsed_at=timezone.now(),
            ocr_confidence=0.92
        )
        assert insurance.ocr_parsed_at is not None
        assert insurance.ocr_confidence == 0.92

    def test_customer_insurance_relationship(self, tenant, customer):
        from apps.customers.models import CustomerInsurance
        CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='MetLife',
            policy_number='M111111'
        )
        CustomerInsurance.objects.create(
            tenant=tenant,
            customer=customer,
            company_name='Travelers',
            policy_number='T222222'
        )
        assert customer.insurance_records.count() == 2
