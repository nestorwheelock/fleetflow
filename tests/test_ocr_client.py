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
from apps.automation.ocr.parsers import (
    LicenseParser,
    InsuranceParser,
    DamageParser,
    DashboardParser,
    ComparisonParser,
)
from apps.automation.ocr.schemas import (
    LicenseOCRResponse,
    InsuranceOCRResponse,
    DamageDetectionResponse,
    DetectedDamage,
    DamageLocation,
    DamageSummary,
    DashboardAnalysisResponse,
    OdometerReading,
    FuelGaugeReading,
    WarningLight,
    DamageComparisonResponse,
    ComparedDamage,
)


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


class TestMultiImageSupport:
    def test_build_multi_image_payload(self):
        client = OpenRouterClient(api_key='test-key')
        images = [
            {'data': b'image1', 'media_type': 'image/jpeg'},
            {'data': b'image2', 'media_type': 'image/png'},
        ]
        payload = client._build_multi_image_payload(
            system_prompt='System prompt',
            user_prompt='User prompt',
            images=images,
            model='anthropic/claude-3.5-sonnet',
        )

        assert payload['model'] == 'anthropic/claude-3.5-sonnet'
        assert payload['max_tokens'] == 4096
        assert payload['temperature'] == 0.1
        assert len(payload['messages']) == 2
        assert payload['messages'][0]['role'] == 'system'
        assert payload['messages'][1]['role'] == 'user'
        content = payload['messages'][1]['content']
        assert len(content) == 3
        assert content[0]['type'] == 'image_url'
        assert content[1]['type'] == 'image_url'
        assert content[2]['type'] == 'text'
        assert content[2]['text'] == 'User prompt'

    def test_build_multi_image_payload_default_media_type(self):
        client = OpenRouterClient(api_key='test-key')
        images = [
            {'data': b'image1'},
        ]
        payload = client._build_multi_image_payload(
            system_prompt='System',
            user_prompt='User',
            images=images,
            model='test-model',
        )

        content = payload['messages'][1]['content']
        assert 'image/jpeg' in content[0]['image_url']['url']

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_send_multi_image_request_success(self, mock_client_class):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"result": "comparison"}'}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {'prompt_tokens': 200, 'completion_tokens': 100},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        images = [
            {'data': b'before', 'media_type': 'image/jpeg'},
            {'data': b'after', 'media_type': 'image/jpeg'},
        ]

        response = client.send_multi_image_request(
            system_prompt='Compare images',
            user_prompt='Find differences',
            images=images,
        )

        assert isinstance(response, VisionResponse)
        assert response.content == '{"result": "comparison"}'

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_send_multi_image_request_auth_error(self, mock_client_class):
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
        images = [{'data': b'image', 'media_type': 'image/jpeg'}]

        with pytest.raises(OpenRouterAuthError):
            client.send_multi_image_request(
                system_prompt='System',
                user_prompt='User',
                images=images,
            )


class TestDamageParser:
    def test_parser_initialization(self):
        client = OpenRouterClient(api_key='test-key')
        parser = DamageParser(client, location='front')

        assert parser.location == 'front'
        assert 'damage' in parser.system_prompt.lower()
        assert parser.response_model == DamageDetectionResponse

    def test_parser_location_property(self):
        client = OpenRouterClient(api_key='test-key')
        parser = DamageParser(client, location='front')

        assert parser.location == 'front'
        parser.location = 'driver_side'
        assert parser.location == 'driver_side'

    def test_parser_user_prompt_includes_location(self):
        client = OpenRouterClient(api_key='test-key')
        parser = DamageParser(client, location='passenger_side')

        assert 'passenger_side' in parser.user_prompt

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_parse_damage_success(self, mock_client_class):
        damage_response = {
            'damages': [
                {
                    'type': 'scratch',
                    'severity': 'minor',
                    'location': {'zone': 'front', 'area': 'bumper'},
                    'description': '6cm scratch on front bumper',
                    'confidence': 0.95,
                }
            ],
            'overall_condition': 'good',
            'summary': {
                'total_count': 1,
                'by_severity': {'minor': 1},
                'by_type': {'scratch': 1},
            },
            'image_quality': 'good',
            'confidence': 0.92,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': json.dumps(damage_response)}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        parser = DamageParser(client, location='front')

        result = parser.parse(b'fake image data')

        assert isinstance(result, DamageDetectionResponse)
        assert result.overall_condition == 'good'
        assert len(result.damages) == 1
        assert result.damages[0].type == 'scratch'
        assert result.damages[0].severity == 'minor'
        assert result.confidence == 0.92


class TestDashboardParser:
    def test_parser_properties(self):
        client = OpenRouterClient(api_key='test-key')
        parser = DashboardParser(client)

        assert 'dashboard' in parser.system_prompt.lower()
        assert parser.response_model == DashboardAnalysisResponse

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_parse_dashboard_success(self, mock_client_class):
        dashboard_response = {
            'odometer': {
                'reading': 45234,
                'unit': 'miles',
                'display_type': 'digital',
                'confidence': 0.98,
            },
            'fuel_gauge': {
                'level': '3/4',
                'percentage': 75,
                'confidence': 0.85,
            },
            'warning_lights': [
                {
                    'indicator': 'check_engine',
                    'status': 'on',
                    'color': 'amber',
                    'confidence': 0.92,
                }
            ],
            'other_indicators': [],
            'image_quality': 'good',
            'confidence': 0.95,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': json.dumps(dashboard_response)}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        parser = DashboardParser(client)

        result = parser.parse(b'fake dashboard image')

        assert isinstance(result, DashboardAnalysisResponse)
        assert result.odometer.reading == 45234
        assert result.odometer.unit == 'miles'
        assert result.fuel_gauge.level == '3/4'
        assert result.fuel_gauge.percentage == 75
        assert len(result.warning_lights) == 1
        assert result.warning_lights[0].indicator == 'check_engine'
        assert result.warning_lights[0].status == 'on'


class TestComparisonParser:
    def test_parser_initialization(self):
        client = OpenRouterClient(api_key='test-key')
        parser = ComparisonParser(client, location='front')

        assert parser.location == 'front'
        assert 'comparison' in parser.system_prompt.lower() or 'compare' in parser.system_prompt.lower()
        assert parser.response_model == DamageComparisonResponse

    def test_parser_location_property(self):
        client = OpenRouterClient(api_key='test-key')
        parser = ComparisonParser(client, location='front')

        assert parser.location == 'front'
        parser.location = 'back'
        assert parser.location == 'back'

    def test_parser_user_prompt_includes_location(self):
        client = OpenRouterClient(api_key='test-key')
        parser = ComparisonParser(client, location='driver_side')

        assert 'driver_side' in parser.user_prompt

    @patch('apps.automation.ocr.client.httpx.Client')
    def test_compare_success(self, mock_client_class):
        comparison_response = {
            'new_damages': [
                {
                    'type': 'dent',
                    'severity': 'moderate',
                    'location': {'zone': 'front', 'area': 'hood'},
                    'description': 'New dent on hood',
                    'confidence': 0.88,
                    'estimated_repair_cost': 350.00,
                }
            ],
            'pre_existing_count': 2,
            'resolved_count': 0,
            'comparison_quality': 'good',
            'summary': '1 new damage detected',
            'confidence': 0.90,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': json.dumps(comparison_response)}}],
            'model': 'anthropic/claude-3.5-sonnet',
            'usage': {},
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key='test-key')
        parser = ComparisonParser(client, location='front')

        result = parser.compare(
            before_image=b'checkout image',
            after_image=b'checkin image',
        )

        assert isinstance(result, DamageComparisonResponse)
        assert len(result.new_damages) == 1
        assert result.new_damages[0].type == 'dent'
        assert result.new_damages[0].severity == 'moderate'
        assert result.pre_existing_count == 2
        assert result.comparison_quality == 'good'


class TestDamageSchemaValidation:
    def test_detected_damage_full(self):
        damage = DetectedDamage(
            type='scratch',
            severity='minor',
            location=DamageLocation(zone='front', area='bumper'),
            description='Small scratch on bumper',
            confidence=0.95,
        )
        assert damage.type == 'scratch'
        assert damage.severity == 'minor'
        assert damage.description == 'Small scratch on bumper'
        assert damage.confidence == 0.95

    def test_detected_damage_with_dimensions(self):
        damage = DetectedDamage(
            type='dent',
            severity='moderate',
            location=DamageLocation(zone='driver_side', area='door'),
            dimensions_estimate={'length_cm': 10.0, 'width_cm': 5.0},
            description='Medium dent on door',
            confidence=0.88,
        )
        assert damage.type == 'dent'
        assert damage.dimensions_estimate['length_cm'] == 10.0

    def test_damage_location(self):
        location = DamageLocation(zone='front', area='bumper')
        assert location.zone == 'front'
        assert location.area == 'bumper'

    def test_damage_location_with_coordinates(self):
        location = DamageLocation(
            zone='front',
            area='bumper',
            coordinates={'x': 45, 'y': 80}
        )
        assert location.coordinates['x'] == 45

    def test_damage_detection_response_defaults(self):
        response = DamageDetectionResponse()
        assert response.damages == []
        assert response.overall_condition == 'unknown'
        assert response.confidence == 0.0

    def test_damage_detection_response_with_damages(self):
        response = DamageDetectionResponse(
            damages=[
                DetectedDamage(
                    type='scratch',
                    severity='minor',
                    location=DamageLocation(zone='front', area='bumper'),
                    description='Small scratch',
                    confidence=0.90,
                ),
                DetectedDamage(
                    type='dent',
                    severity='moderate',
                    location=DamageLocation(zone='back', area='trunk'),
                    description='Medium dent',
                    confidence=0.85,
                ),
            ],
            overall_condition='fair',
            confidence=0.88,
        )
        assert len(response.damages) == 2
        assert response.overall_condition == 'fair'

    def test_damage_summary(self):
        summary = DamageSummary(
            total_count=3,
            by_severity={'minor': 2, 'moderate': 1},
            by_type={'scratch': 2, 'dent': 1},
        )
        assert summary.total_count == 3
        assert summary.by_severity['minor'] == 2


class TestDashboardSchemaValidation:
    def test_odometer_reading(self):
        odometer = OdometerReading(
            reading=45234,
            unit='miles',
            display_type='digital',
            confidence=0.98,
        )
        assert odometer.reading == 45234
        assert odometer.unit == 'miles'

    def test_odometer_reading_with_defaults(self):
        odometer = OdometerReading(reading=50000, confidence=0.95)
        assert odometer.reading == 50000
        assert odometer.unit == 'miles'
        assert odometer.display_type == 'digital'

    def test_fuel_gauge_reading(self):
        fuel = FuelGaugeReading(
            level='3/4',
            percentage=75,
            confidence=0.85,
        )
        assert fuel.level == '3/4'
        assert fuel.percentage == 75

    def test_warning_light(self):
        warning = WarningLight(
            indicator='check_engine',
            status='on',
            color='amber',
            confidence=0.92,
        )
        assert warning.indicator == 'check_engine'
        assert warning.status == 'on'
        assert warning.color == 'amber'

    def test_dashboard_analysis_response_defaults(self):
        response = DashboardAnalysisResponse()
        assert response.odometer is None
        assert response.fuel_gauge is None
        assert response.warning_lights == []
        assert response.other_indicators == []

    def test_dashboard_analysis_with_full_data(self):
        response = DashboardAnalysisResponse(
            odometer=OdometerReading(reading=50000, confidence=0.98),
            fuel_gauge=FuelGaugeReading(level='1/2', percentage=50),
            warning_lights=[
                WarningLight(indicator='tire_pressure', status='on'),
            ],
            confidence=0.95,
        )
        assert response.odometer.reading == 50000
        assert response.fuel_gauge.percentage == 50
        assert len(response.warning_lights) == 1


class TestComparisonSchemaValidation:
    def test_compared_damage_full(self):
        damage = ComparedDamage(
            type='dent',
            severity='moderate',
            location={'zone': 'front', 'area': 'hood'},
            description='New dent on hood',
            confidence=0.88,
        )
        assert damage.type == 'dent'
        assert damage.severity == 'moderate'
        assert damage.location['zone'] == 'front'

    def test_compared_damage_with_repair_cost(self):
        damage = ComparedDamage(
            type='scratch',
            severity='minor',
            location={'zone': 'back', 'area': 'bumper'},
            description='New scratch',
            estimated_repair_cost=150.00,
            confidence=0.92,
        )
        assert damage.type == 'scratch'
        assert damage.estimated_repair_cost == 150.00

    def test_damage_comparison_response_defaults(self):
        response = DamageComparisonResponse()
        assert response.new_damages == []
        assert response.pre_existing_count == 0
        assert response.resolved_count == 0
        assert response.comparison_quality == 'unknown'

    def test_damage_comparison_response_with_damages(self):
        response = DamageComparisonResponse(
            new_damages=[
                ComparedDamage(
                    type='scratch',
                    severity='minor',
                    location={'zone': 'front', 'area': 'bumper'},
                    description='New scratch on front bumper',
                    confidence=0.88,
                ),
            ],
            pre_existing_count=2,
            resolved_count=1,
            comparison_quality='good',
            summary='1 new scratch detected',
            confidence=0.92,
        )
        assert len(response.new_damages) == 1
        assert response.pre_existing_count == 2
        assert response.resolved_count == 1
        assert response.comparison_quality == 'good'

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            DamageComparisonResponse(confidence=1.5)

        with pytest.raises(Exception):
            DamageDetectionResponse(confidence=-0.1)
