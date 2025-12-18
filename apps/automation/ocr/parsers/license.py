"""
Driver's license OCR parser.
"""
from typing import Type

from ..client import OpenRouterClient
from ..prompts.license import LICENSE_OCR_SYSTEM_PROMPT, LICENSE_OCR_USER_PROMPT
from ..schemas.license import LicenseOCRResponse
from .base import BaseDocumentParser


class LicenseParser(BaseDocumentParser[LicenseOCRResponse]):
    """Parser for driver's license images."""

    @property
    def system_prompt(self) -> str:
        return LICENSE_OCR_SYSTEM_PROMPT

    @property
    def user_prompt(self) -> str:
        return LICENSE_OCR_USER_PROMPT

    @property
    def response_model(self) -> Type[LicenseOCRResponse]:
        return LicenseOCRResponse


def create_license_parser(
    api_key: str,
    model: str = 'anthropic/claude-3.5-sonnet',
    **kwargs,
) -> LicenseParser:
    """Factory function to create a configured LicenseParser.

    Args:
        api_key: OpenRouter API key
        model: Vision model to use
        **kwargs: Additional arguments passed to OpenRouterClient

    Returns:
        Configured LicenseParser instance
    """
    client = OpenRouterClient(api_key=api_key, model=model, **kwargs)
    return LicenseParser(client)
