"""
Vehicle damage comparison parser.

Portability Note: This parser can be used in any before/after vehicle comparison context.
"""
import logging
from typing import Type

from pydantic import ValidationError

from ..client import OpenRouterClient, VisionResponse
from ..prompts.comparison import COMPARISON_SYSTEM_PROMPT, COMPARISON_USER_PROMPT
from ..schemas.comparison import DamageComparisonResponse

logger = logging.getLogger(__name__)


class ComparisonParser:
    """Parser for comparing two vehicle photos (before/after).

    Unlike other parsers, this one accepts TWO images - a "before" (checkout)
    and "after" (checkin) photo of the same area - and identifies new damage.

    Portability Note: This parser is designed to work with any before/after
    vehicle comparison use case - rental returns, fleet returns, accident
    assessment, insurance claims, etc.
    """

    def __init__(self, client: OpenRouterClient, location: str = 'exterior'):
        """Initialize the comparison parser.

        Args:
            client: Configured OpenRouterClient instance
            location: Photo location being compared (front, back, etc.)
        """
        self.client = client
        self._location = location

    @property
    def location(self) -> str:
        """Return the photo location."""
        return self._location

    @location.setter
    def location(self, value: str):
        """Set the photo location."""
        self._location = value

    @property
    def system_prompt(self) -> str:
        return COMPARISON_SYSTEM_PROMPT

    @property
    def user_prompt(self) -> str:
        return COMPARISON_USER_PROMPT.format(location=self._location)

    @property
    def response_model(self) -> Type[DamageComparisonResponse]:
        return DamageComparisonResponse

    def compare(
        self,
        before_image: bytes,
        after_image: bytes,
        before_media_type: str = 'image/jpeg',
        after_media_type: str = 'image/jpeg',
        model: str | None = None,
    ) -> DamageComparisonResponse:
        """Compare two vehicle photos synchronously.

        Args:
            before_image: Raw bytes of the "before" (checkout) image
            after_image: Raw bytes of the "after" (checkin) image
            before_media_type: MIME type of the before image
            after_media_type: MIME type of the after image
            model: Optional model override

        Returns:
            Comparison response with identified new damages

        Raises:
            ValueError: If response cannot be parsed or validated
            OpenRouterError: For API errors
        """
        response = self.client.send_multi_image_request(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
            images=[
                {'data': before_image, 'media_type': before_media_type},
                {'data': after_image, 'media_type': after_media_type},
            ],
            model=model or self.client.model,
        )
        return self._process_response(response)

    async def compare_async(
        self,
        before_image: bytes,
        after_image: bytes,
        before_media_type: str = 'image/jpeg',
        after_media_type: str = 'image/jpeg',
        model: str | None = None,
    ) -> DamageComparisonResponse:
        """Compare two vehicle photos asynchronously.

        Args:
            before_image: Raw bytes of the "before" (checkout) image
            after_image: Raw bytes of the "after" (checkin) image
            before_media_type: MIME type of the before image
            after_media_type: MIME type of the after image
            model: Optional model override

        Returns:
            Comparison response with identified new damages

        Raises:
            ValueError: If response cannot be parsed or validated
            OpenRouterError: For API errors
        """
        response = await self.client.send_multi_image_request_async(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
            images=[
                {'data': before_image, 'media_type': before_media_type},
                {'data': after_image, 'media_type': after_media_type},
            ],
            model=model or self.client.model,
        )
        return self._process_response(response)

    def _process_response(self, response: VisionResponse) -> DamageComparisonResponse:
        """Process and validate the API response.

        Args:
            response: Raw API response

        Returns:
            Validated comparison response model

        Raises:
            ValueError: If response cannot be parsed or validated
        """
        try:
            json_data = self.client.extract_json_from_response(response.content)
        except ValueError as e:
            logger.error(f'Failed to extract JSON from response: {e}')
            logger.debug(f'Raw response content: {response.content}')
            raise

        try:
            return self.response_model.model_validate(json_data)
        except ValidationError as e:
            logger.error(f'Response validation failed: {e}')
            logger.debug(f'JSON data: {json_data}')
            raise ValueError(f'Response validation failed: {e}') from e


def create_comparison_parser(
    api_key: str,
    location: str = 'exterior',
    model: str = 'anthropic/claude-3.5-sonnet',
    **kwargs,
) -> ComparisonParser:
    """Factory function to create a configured ComparisonParser.

    Args:
        api_key: OpenRouter API key
        location: Photo location being compared (front, back, etc.)
        model: Vision model to use
        **kwargs: Additional arguments passed to OpenRouterClient

    Returns:
        Configured ComparisonParser instance
    """
    client = OpenRouterClient(api_key=api_key, model=model, **kwargs)
    return ComparisonParser(client, location=location)
