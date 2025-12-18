"""
Vehicle damage detection parser.

Portability Note: This parser can be used in any vehicle inspection context.
"""
from typing import Type

from ..client import OpenRouterClient
from ..prompts.damage import DAMAGE_DETECTION_SYSTEM_PROMPT, DAMAGE_DETECTION_USER_PROMPT
from ..schemas.damage import DamageDetectionResponse
from .base import BaseDocumentParser


class DamageParser(BaseDocumentParser[DamageDetectionResponse]):
    """Parser for vehicle damage detection from photos.

    Analyzes vehicle photos to identify scratches, dents, cracks, chips,
    stains, tears, missing parts, rust, and other damage.

    Portability Note: This parser is designed to work with any vehicle
    inspection use case - rental returns, fleet management, insurance,
    personal vehicle tracking, etc.
    """

    def __init__(self, client: OpenRouterClient, location: str = 'exterior'):
        """Initialize the damage parser.

        Args:
            client: Configured OpenRouterClient instance
            location: Photo location (front, back, driver_side, etc.)
        """
        super().__init__(client)
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
        return DAMAGE_DETECTION_SYSTEM_PROMPT

    @property
    def user_prompt(self) -> str:
        return DAMAGE_DETECTION_USER_PROMPT.format(location=self._location)

    @property
    def response_model(self) -> Type[DamageDetectionResponse]:
        return DamageDetectionResponse


def create_damage_parser(
    api_key: str,
    location: str = 'exterior',
    model: str = 'anthropic/claude-3.5-sonnet',
    **kwargs,
) -> DamageParser:
    """Factory function to create a configured DamageParser.

    Args:
        api_key: OpenRouter API key
        location: Photo location (front, back, driver_side, interior, etc.)
        model: Vision model to use
        **kwargs: Additional arguments passed to OpenRouterClient

    Returns:
        Configured DamageParser instance
    """
    client = OpenRouterClient(api_key=api_key, model=model, **kwargs)
    return DamageParser(client, location=location)
