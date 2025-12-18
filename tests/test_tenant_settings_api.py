import pytest
from unittest.mock import patch, Mock
from django.test import Client
from rest_framework.test import APIClient

from apps.tenants.models import TenantSettings
from apps.automation.ocr.utils.encryption import reset_encryption_key_cache


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, tenant_user):
    api_client.force_authenticate(user=tenant_user.user)
    return api_client


@pytest.fixture
def staff_user(db, tenant):
    from django.contrib.auth import get_user_model
    from apps.tenants.models import TenantUser
    User = get_user_model()
    user = User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='staffpass123'
    )
    tenant_user = TenantUser.objects.create(
        tenant=tenant,
        user=user,
        role='staff'
    )
    return tenant_user


@pytest.fixture
def staff_api_client(api_client, staff_user):
    api_client.force_authenticate(user=staff_user.user)
    return api_client


@pytest.mark.django_db
class TestTenantSettingsAPI:
    def test_get_settings_unauthenticated(self, api_client):
        response = api_client.get('/api/tenants/settings/')
        assert response.status_code == 403

    def test_get_settings_creates_if_not_exists(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        assert not TenantSettings.objects.filter(tenant=tenant).exists()

        response = authenticated_api_client.get('/api/tenants/settings/')
        assert response.status_code == 200

        assert TenantSettings.objects.filter(tenant=tenant).exists()

    def test_get_settings_returns_data(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        TenantSettings.objects.create(
            tenant=tenant,
            openrouter_enabled=True,
            openrouter_model='anthropic/claude-3.5-sonnet',
            auto_parse_license=True,
            auto_parse_insurance=False
        )

        response = authenticated_api_client.get('/api/tenants/settings/')
        assert response.status_code == 200

        data = response.json()
        assert data['openrouter_enabled'] is True
        assert data['openrouter_model'] == 'anthropic/claude-3.5-sonnet'
        assert data['auto_parse_license'] is True
        assert data['auto_parse_insurance'] is False
        assert data['has_api_key'] is False
        assert 'api_key' not in data

    def test_update_settings_as_owner(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        TenantSettings.objects.create(tenant=tenant)

        response = authenticated_api_client.patch(
            '/api/tenants/settings/',
            {
                'openrouter_enabled': True,
                'auto_parse_license': True,
                'auto_parse_insurance': True
            },
            format='json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['openrouter_enabled'] is True
        assert data['auto_parse_license'] is True
        assert data['auto_parse_insurance'] is True

    def test_update_settings_denied_for_staff(self, staff_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        TenantSettings.objects.create(tenant=tenant)

        response = staff_api_client.patch(
            '/api/tenants/settings/',
            {'openrouter_enabled': True},
            format='json'
        )

        assert response.status_code == 403
        assert 'owner' in response.json()['error'].lower()

    def test_set_api_key(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        TenantSettings.objects.create(tenant=tenant)

        response = authenticated_api_client.patch(
            '/api/tenants/settings/',
            {'api_key': 'sk-or-v1-test-api-key'},
            format='json'
        )

        assert response.status_code == 200
        assert response.json()['has_api_key'] is True

        tenant_settings = TenantSettings.objects.get(tenant=tenant)
        assert tenant_settings.get_api_key() == 'sk-or-v1-test-api-key'

    def test_clear_api_key(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        tenant_settings = TenantSettings.objects.create(tenant=tenant)
        tenant_settings.set_api_key('sk-or-existing-key')
        tenant_settings.save()

        response = authenticated_api_client.patch(
            '/api/tenants/settings/',
            {'api_key': ''},
            format='json'
        )

        assert response.status_code == 200
        assert response.json()['has_api_key'] is False

        tenant_settings.refresh_from_db()
        assert tenant_settings.get_api_key() is None

    def test_can_use_ocr_field(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        tenant.plan = 'starter'
        tenant.save()

        TenantSettings.objects.create(tenant=tenant, openrouter_enabled=True)

        response = authenticated_api_client.get('/api/tenants/settings/')
        assert response.status_code == 200
        assert response.json()['can_use_ocr'] is False

        tenant.plan = 'professional'
        tenant.save()

        tenant_settings = TenantSettings.objects.get(tenant=tenant)
        tenant_settings.set_api_key('sk-or-test-key')
        tenant_settings.save()

        response = authenticated_api_client.get('/api/tenants/settings/')
        assert response.status_code == 200
        assert response.json()['can_use_ocr'] is True


@pytest.mark.django_db
class TestAPIKeyValidation:
    @patch('apps.tenants.views.httpx.Client')
    def test_test_api_key_valid(self, mock_client_class, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'label': 'Test Key',
                'limit': 100,
                'usage': 10
            }
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        response = authenticated_api_client.post(
            '/api/tenants/settings/test-api-key/',
            {'api_key': 'sk-or-test-key'},
            format='json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert data['label'] == 'Test Key'

    @patch('apps.tenants.views.httpx.Client')
    def test_test_api_key_invalid(self, mock_client_class, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        mock_response = Mock()
        mock_response.status_code = 401

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        response = authenticated_api_client.post(
            '/api/tenants/settings/test-api-key/',
            {'api_key': 'invalid-key'},
            format='json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is False
        assert 'authentication' in data['error'].lower()

    def test_test_api_key_no_key_provided(self, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        response = authenticated_api_client.post(
            '/api/tenants/settings/test-api-key/',
            {},
            format='json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['valid'] is False
        assert 'no api key' in data['error'].lower()

    @patch('apps.tenants.views.httpx.Client')
    def test_test_api_key_uses_stored_key(self, mock_client_class, authenticated_api_client, tenant, settings):
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        tenant_settings = TenantSettings.objects.create(tenant=tenant)
        tenant_settings.set_api_key('sk-or-stored-key')
        tenant_settings.save()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {}}

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        response = authenticated_api_client.post(
            '/api/tenants/settings/test-api-key/',
            {},
            format='json'
        )

        assert response.status_code == 200
        assert response.json()['valid'] is True

        call_args = mock_client.get.call_args
        assert 'Bearer sk-or-stored-key' in str(call_args)

    @patch('apps.tenants.views.httpx.Client')
    def test_test_api_key_timeout(self, mock_client_class, authenticated_api_client, tenant, settings):
        import httpx
        settings.FIELD_ENCRYPTION_KEY = 'test-key-for-settings-api'
        reset_encryption_key_cache()

        mock_client = Mock()
        mock_client.get.side_effect = httpx.TimeoutException('Timeout')
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        response = authenticated_api_client.post(
            '/api/tenants/settings/test-api-key/',
            {'api_key': 'sk-or-test-key'},
            format='json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is False
        assert 'timeout' in data['error'].lower()
