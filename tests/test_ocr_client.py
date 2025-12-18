import pytest
import json
from unittest.mock import Mock, patch, AsyncMock

from apps.automation.ocr.client import (
    OpenRouterClient,
    OpenRouterError,
    OpenRouterAPIError,
    OpenRouterAuthError,
    OpenRouterRateLimitError,
    VisionRequest,
    VisionResponse,
    encode_image_base64,
)
from apps.automation.ocr.parsers import LicenseParser, InsuranceParser
from apps.automation.ocr.schemas import LicenseOCRResponse, InsuranceOCRResponse


class TestOpenRouterClient:
    def test_client_initialization(self):
        client = OpenRouterClient(
            api_key='test-api-key',
            model='anthropic/claude-3.5-sonnet',
            timeout=30.0,
            site_url='https://example.com',
            site_name='Test App',
        )
        assert client.api_key == 'test-api-key'
        assert client.model == 'anthropic/claude-3.5-sonnet'
        assert client.timeout == 30.0
        assert client.site_url == 'https://example.com'
        assert client.site_name == 'Test App'

    def test_build_headers(self):
        client = OpenRouterClient(
            api_key='test-api-key',
            site_url='https://example.com',
            site_name='Test App',
        )
        headers = client._build_headers()
        assert headers['Authorization'] == 'Bearer test-api-key'
        assert headers['Content-Type'] == 'application/json'
        assert headers['HTTP-Referer'] == 'https://example.com'
        assert headers['X-Title'] == 'Test App'

    def test_build_headers_minimal(self):
        client = OpenRouterClient(api_key='test-api-key')
        headers = client._build_headers()
        assert headers['Authorization'] == 'Bearer test-api-key'
        assert 'HTTP-Referer' not in headers
        assert 'X-Title' not in headers

    def test_encode_image_base64(self):
        image_data = b'fake image data'
        encoded = encode_image_base64(image_data)
        assert isinstance(encoded, str)
        assert encoded == 'ZmFrZSBpbWFnZSBkYXRh'

    def test_build_vision_payload(self):
        client = OpenRouterClient(api_key='test-api-key')
        request = VisionRequest(
            system_prompt='You are an OCR expert.',
            user_prompt='Extract text from this image.',
            image_data=b'fake image',
            image_media_type='image/jpeg',
            model='anthropic/claude-3.5-sonnet',
            max_tokens=4096,
            temperature=0.1,
        )
        payload = client._build_vision_payload(request)

        assert payload['model'] == 'anthropic/claude-3.5-sonnet'
        assert payload['max_tokens'] == 4096
        assert payload['temperature'] == 0.1
        assert len(payload['messages']) == 2
        assert payload['messages'][0]['role'] == 'system'
        assert payload['messages'][0]['content'] == 'You are an OCR expert.'
        assert payload['messages'][1]['role'] == 'user'
        assert len(payload['messages'][1]['content']) == 2

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_send_vision_request_success(self, mock_client_class):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"result": "success"}'}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {'prompt_tokens': 100, 'completion_tokens': 50},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-api-key')
        request = VisionRequest(
            system_prompt='System',
            user_prompt='User',
            image_data=b'image',
        )

        response = client.send_vision_request(request)

        assert isinstance(response, VisionResponse)
        assert response.content == '{"result": "success"}'
        assert response.model == 'anthropic/claude-3.5-sonnet'
        assert response.usage['prompt_tokens'] == 100

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_send_vision_request_auth_error(self, mock_client_class):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_response.json.return_value = {'error': {'message': 'Invalid API key'}}

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='invalid-key')
        request = VisionRequest(
            system_prompt='System',
            user_prompt='User',
            image_data=b'image',
        )

        with pytest.raises(OpenRouterAuthError) as exc_info:
            client.send_vision_request(request)

        assert exc_info.value.status_code == 401

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_send_vision_request_rate_limit_error(self, mock_client_class):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = 'Rate limited'
        mock_response.json.return_value = {'error': {'message': 'Rate limit exceeded'}}

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        request = VisionRequest(
            system_prompt='System',
            user_prompt='User',
            image_data=b'image',
        )

        with pytest.raises(OpenRouterRateLimitError) as exc_info:
            client.send_vision_request(request)

        assert exc_info.value.status_code == 429

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_send_vision_request_api_error(self, mock_client_class):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_response.json.return_value = {'error': {'message': 'Server error'}}

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        request = VisionRequest(
            system_prompt='System',
            user_prompt='User',
            image_data=b'image',
        )

        with pytest.raises(OpenRouterAPIError) as exc_info:
            client.send_vision_request(request)

        assert exc_info.value.status_code == 500

    def test_extract_json_from_response_plain(self):
        client = OpenRouterClient(api_key='test-key')
        content = '{"name": "John", "age": 30}'
        result = client.extract_json_from_response(content)
        assert result == {'name': 'John', 'age': 30}

    def test_extract_json_from_response_with_markdown(self):
        client = OpenRouterClient(api_key='test-key')
        content = '```json\n{"name": "John", "age": 30}\n```'
        result = client.extract_json_from_response(content)
        assert result == {'name': 'John', 'age': 30}

    def test_extract_json_from_response_with_extra_text(self):
        client = OpenRouterClient(api_key='test-key')
        content = 'Here is the result:\n{"name": "John"}\nThat is all.'
        result = client.extract_json_from_response(content)
        assert result == {'name': 'John'}

    def test_extract_json_from_response_invalid(self):
        client = OpenRouterClient(api_key='test-key')
        content = 'This is not JSON'
        with pytest.raises(ValueError):
            client.extract_json_from_response(content)


class TestLicenseParser:
    def test_parser_properties(self):
        client = OpenRouterClient(api_key='test-key')
        parser = LicenseParser(client)

        assert 'driver' in parser.system_prompt.lower() or 'license' in parser.system_prompt.lower()
        assert parser.response_model == LicenseOCRResponse

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_parse_license_success(self, mock_client_class):
        license_response = {
            'country': 'USA',
            'issuing_authority': 'Texas',
            'license_number': 'DL12345678',
            'license_class': 'C',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1985-05-15',
            'confidence': 0.95,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': json.dumps(license_response)}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        parser = LicenseParser(client)

        result = parser.parse(b'fake image data')

        assert isinstance(result, LicenseOCRResponse)
        assert result.country == 'USA'
        assert result.issuing_authority == 'Texas'
        assert result.license_number == 'DL12345678'
        assert result.first_name == 'John'
        assert result.last_name == 'Doe'
        assert result.confidence == 0.95


class TestInsuranceParser:
    def test_parser_properties(self):
        client = OpenRouterClient(api_key='test-key')
        parser = InsuranceParser(client)

        assert 'insurance' in parser.system_prompt.lower()
        assert parser.response_model == InsuranceOCRResponse

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_parse_insurance_success(self, mock_client_class):
        insurance_response = {
            'company_name': 'State Farm',
            'policy_number': 'SF123456789',
            'effective_date': '2024-01-01',
            'expiration_date': '2025-01-01',
            'policyholder_name': 'John Doe',
            'coverage_type': 'full',
            'confidence': 0.92,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': json.dumps(insurance_response)}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        parser = InsuranceParser(client)

        result = parser.parse(b'fake image data')

        assert isinstance(result, InsuranceOCRResponse)
        assert result.company_name == 'State Farm'
        assert result.policy_number == 'SF123456789'
        assert result.policyholder_name == 'John Doe'
        assert result.confidence == 0.92


class TestSchemaValidation:
    def test_license_schema_defaults(self):
        response = LicenseOCRResponse()
        assert response.country == 'USA'
        assert response.first_name == ''
        assert response.confidence == 0.0
        assert response.has_photo is False

    def test_license_schema_with_data(self):
        response = LicenseOCRResponse(
            country='USA',
            issuing_authority='California',
            license_number='CA123456',
            first_name='Jane',
            last_name='Smith',
            confidence=0.88,
        )
        assert response.issuing_authority == 'California'
        assert response.first_name == 'Jane'

    def test_insurance_schema_defaults(self):
        response = InsuranceOCRResponse()
        assert response.company_name == ''
        assert response.policy_number == ''
        assert response.covered_vehicles == []
        assert response.confidence == 0.0

    def test_insurance_schema_with_vehicles(self):
        response = InsuranceOCRResponse(
            company_name='Geico',
            policy_number='G12345',
            covered_vehicles=[
                {'year': 2023, 'make': 'Toyota', 'model': 'Camry', 'vin': 'ABC123'}
            ],
        )
        assert len(response.covered_vehicles) == 1
        assert response.covered_vehicles[0].make == 'Toyota'

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            LicenseOCRResponse(confidence=1.5)

        with pytest.raises(Exception):
            LicenseOCRResponse(confidence=-0.1)
