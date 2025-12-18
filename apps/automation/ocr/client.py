"""
OpenRouter API client for vision model requests.

This module provides a portable, framework-independent client for interacting
with the OpenRouter API for OCR and image analysis tasks.
"""
import base64
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
DEFAULT_MODEL = 'anthropic/claude-3.5-sonnet'
DEFAULT_TIMEOUT = 60.0


class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors."""
    pass


class OpenRouterAPIError(OpenRouterError):
    """Exception for API-level errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class OpenRouterRateLimitError(OpenRouterAPIError):
    """Exception for rate limit errors."""
    pass


class OpenRouterAuthError(OpenRouterAPIError):
    """Exception for authentication errors."""
    pass


@dataclass
class VisionRequest:
    """Request structure for vision model API calls."""
    system_prompt: str
    user_prompt: str
    image_data: bytes
    image_media_type: str = 'image/jpeg'
    model: str = DEFAULT_MODEL
    max_tokens: int = 4096
    temperature: float = 0.1


@dataclass
class VisionResponse:
    """Response structure from vision model API calls."""
    content: str
    model: str
    usage: dict
    raw_response: dict


def encode_image_base64(image_data: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_data).decode('utf-8')


def load_image_from_path(path: Union[str, Path]) -> tuple[bytes, str]:
    """Load image from file path and determine media type.

    Args:
        path: Path to the image file

    Returns:
        Tuple of (image_bytes, media_type)
    """
    path = Path(path)
    suffix = path.suffix.lower()

    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }

    media_type = media_types.get(suffix, 'image/jpeg')

    with open(path, 'rb') as f:
        image_data = f.read()

    return image_data, media_type


class OpenRouterClient:
    """Client for making vision model requests to OpenRouter API."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Default model to use for requests
            timeout: Request timeout in seconds
            site_url: Optional site URL for OpenRouter analytics
            site_name: Optional site name for OpenRouter analytics
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.site_url = site_url
        self.site_name = site_name

    def _build_headers(self) -> dict:
        """Build request headers."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        if self.site_url:
            headers['HTTP-Referer'] = self.site_url
        if self.site_name:
            headers['X-Title'] = self.site_name
        return headers

    def _build_vision_payload(self, request: VisionRequest) -> dict:
        """Build the API payload for a vision request."""
        image_base64 = encode_image_base64(request.image_data)

        return {
            'model': request.model or self.model,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature,
            'messages': [
                {
                    'role': 'system',
                    'content': request.system_prompt,
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:{request.image_media_type};base64,{image_base64}',
                            },
                        },
                        {
                            'type': 'text',
                            'text': request.user_prompt,
                        },
                    ],
                },
            ],
        }

    def _build_multi_image_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        images: list[dict],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> dict:
        """Build the API payload for a multi-image vision request.

        Args:
            system_prompt: System prompt for the model
            user_prompt: User prompt for the model
            images: List of dicts with 'data' (bytes) and 'media_type' (str) keys
            model: Model to use for the request
            max_tokens: Maximum tokens in response
            temperature: Model temperature

        Returns:
            API payload dictionary
        """
        content = []

        for image in images:
            image_base64 = encode_image_base64(image['data'])
            media_type = image.get('media_type', 'image/jpeg')
            content.append({
                'type': 'image_url',
                'image_url': {
                    'url': f'data:{media_type};base64,{image_base64}',
                },
            })

        content.append({
            'type': 'text',
            'text': user_prompt,
        })

        return {
            'model': model or self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt,
                },
                {
                    'role': 'user',
                    'content': content,
                },
            ],
        }

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_body = response.json()
            error_message = error_body.get('error', {}).get('message', response.text)
        except Exception:
            error_message = response.text

        if response.status_code == 401:
            raise OpenRouterAuthError(
                f'Authentication failed: {error_message}',
                status_code=response.status_code,
                response_body=response.text,
            )
        elif response.status_code == 429:
            raise OpenRouterRateLimitError(
                f'Rate limit exceeded: {error_message}',
                status_code=response.status_code,
                response_body=response.text,
            )
        else:
            raise OpenRouterAPIError(
                f'API request failed: {error_message}',
                status_code=response.status_code,
                response_body=response.text,
            )

    def send_vision_request(self, request: VisionRequest) -> VisionResponse:
        """Send a synchronous vision request to the API.

        Args:
            request: VisionRequest object containing the request details

        Returns:
            VisionResponse object with the API response

        Raises:
            OpenRouterAuthError: If authentication fails
            OpenRouterRateLimitError: If rate limit is exceeded
            OpenRouterAPIError: For other API errors
        """
        headers = self._build_headers()
        payload = self._build_vision_payload(request)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            self._handle_error_response(response)

        data = response.json()

        return VisionResponse(
            content=data['choices'][0]['message']['content'],
            model=data.get('model', request.model),
            usage=data.get('usage', {}),
            raw_response=data,
        )

    async def send_vision_request_async(self, request: VisionRequest) -> VisionResponse:
        """Send an asynchronous vision request to the API.

        Args:
            request: VisionRequest object containing the request details

        Returns:
            VisionResponse object with the API response

        Raises:
            OpenRouterAuthError: If authentication fails
            OpenRouterRateLimitError: If rate limit is exceeded
            OpenRouterAPIError: For other API errors
        """
        headers = self._build_headers()
        payload = self._build_vision_payload(request)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            self._handle_error_response(response)

        data = response.json()

        return VisionResponse(
            content=data['choices'][0]['message']['content'],
            model=data.get('model', request.model),
            usage=data.get('usage', {}),
            raw_response=data,
        )

    def send_multi_image_request(
        self,
        system_prompt: str,
        user_prompt: str,
        images: list[dict],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> VisionResponse:
        """Send a synchronous multi-image vision request to the API.

        Portability Note: This method is designed for comparison tasks that require
        analyzing multiple images together (e.g., before/after comparison).

        Args:
            system_prompt: System prompt for the model
            user_prompt: User prompt for the model
            images: List of dicts with 'data' (bytes) and 'media_type' (str) keys
            model: Optional model override
            max_tokens: Maximum tokens in response
            temperature: Model temperature

        Returns:
            VisionResponse object with the API response

        Raises:
            OpenRouterAuthError: If authentication fails
            OpenRouterRateLimitError: If rate limit is exceeded
            OpenRouterAPIError: For other API errors
        """
        headers = self._build_headers()
        payload = self._build_multi_image_payload(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            images=images,
            model=model or self.model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            self._handle_error_response(response)

        data = response.json()

        return VisionResponse(
            content=data['choices'][0]['message']['content'],
            model=data.get('model', model or self.model),
            usage=data.get('usage', {}),
            raw_response=data,
        )

    async def send_multi_image_request_async(
        self,
        system_prompt: str,
        user_prompt: str,
        images: list[dict],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> VisionResponse:
        """Send an asynchronous multi-image vision request to the API.

        Portability Note: This method is designed for comparison tasks that require
        analyzing multiple images together (e.g., before/after comparison).

        Args:
            system_prompt: System prompt for the model
            user_prompt: User prompt for the model
            images: List of dicts with 'data' (bytes) and 'media_type' (str) keys
            model: Optional model override
            max_tokens: Maximum tokens in response
            temperature: Model temperature

        Returns:
            VisionResponse object with the API response

        Raises:
            OpenRouterAuthError: If authentication fails
            OpenRouterRateLimitError: If rate limit is exceeded
            OpenRouterAPIError: For other API errors
        """
        headers = self._build_headers()
        payload = self._build_multi_image_payload(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            images=images,
            model=model or self.model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            self._handle_error_response(response)

        data = response.json()

        return VisionResponse(
            content=data['choices'][0]['message']['content'],
            model=data.get('model', model or self.model),
            usage=data.get('usage', {}),
            raw_response=data,
        )

    def extract_json_from_response(self, content: str) -> dict:
        """Extract JSON from model response content.

        Models sometimes wrap JSON in markdown code blocks or add extra text.
        This method attempts to extract the JSON object.

        Args:
            content: Raw content string from the model

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If no valid JSON can be extracted
        """
        content = content.strip()

        if content.startswith('```'):
            lines = content.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith('```') and not in_json:
                    in_json = True
                    continue
                elif line.startswith('```') and in_json:
                    break
                elif in_json:
                    json_lines.append(line)
            content = '\n'.join(json_lines)

        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx != -1 and end_idx != -1:
            content = content[start_idx:end_idx + 1]

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f'Failed to parse JSON from response: {e}') from e
