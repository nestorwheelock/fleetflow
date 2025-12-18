"""
Base parser class for OCR document parsing.
"""
import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type

from pydantic import BaseModel, ValidationError

from ..client import OpenRouterClient, VisionRequest, VisionResponse

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class BaseDocumentParser(ABC, Generic[T]):
    """Abstract base class for document parsers."""

    def __init__(self, client: OpenRouterClient):
        """Initialize the parser with an OpenRouter client.

        Args:
            client: Configured OpenRouterClient instance
        """
        self.client = client

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this parser."""
        pass

    @property
    @abstractmethod
    def user_prompt(self) -> str:
        """Return the user prompt for this parser."""
        pass

    @property
    @abstractmethod
    def response_model(self) -> Type[T]:
        """Return the Pydantic model for response validation."""
        pass

    def parse(
        self,
        image_data: bytes,
        image_media_type: str = 'image/jpeg',
        model: str | None = None,
    ) -> T:
        """Parse a document image synchronously.

        Args:
            image_data: Raw image bytes
            image_media_type: MIME type of the image
            model: Optional model override

        Returns:
            Parsed and validated response object

        Raises:
            ValueError: If response cannot be parsed or validated
            OpenRouterError: For API errors
        """
        request = VisionRequest(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
            image_data=image_data,
            image_media_type=image_media_type,
            model=model or self.client.model,
        )

        response = self.client.send_vision_request(request)
        return self._process_response(response)

    async def parse_async(
        self,
        image_data: bytes,
        image_media_type: str = 'image/jpeg',
        model: str | None = None,
    ) -> T:
        """Parse a document image asynchronously.

        Args:
            image_data: Raw image bytes
            image_media_type: MIME type of the image
            model: Optional model override

        Returns:
            Parsed and validated response object

        Raises:
            ValueError: If response cannot be parsed or validated
            OpenRouterError: For API errors
        """
        request = VisionRequest(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
            image_data=image_data,
            image_media_type=image_media_type,
            model=model or self.client.model,
        )

        response = await self.client.send_vision_request_async(request)
        return self._process_response(response)

    def _process_response(self, response: VisionResponse) -> T:
        """Process and validate the API response.

        Args:
            response: Raw API response

        Returns:
            Validated response model

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
