"""
Insurance card OCR parser.
"""
from typing import Type

from ..client import OpenRouterClient
from ..prompts.insurance import INSURANCE_OCR_SYSTEM_PROMPT, INSURANCE_OCR_USER_PROMPT
from ..schemas.insurance import InsuranceOCRResponse
from .base import BaseDocumentParser


class InsuranceParser(BaseDocumentParser[InsuranceOCRResponse]):
    """Parser for insurance card images."""

    @property
    def system_prompt(self) -> str:
        return INSURANCE_OCR_SYSTEM_PROMPT

    @property
    def user_prompt(self) -> str:
        return INSURANCE_OCR_USER_PROMPT

    @property
    def response_model(self) -> Type[InsuranceOCRResponse]:
        return InsuranceOCRResponse


def create_insurance_parser(
    api_key: str,
    model: str = 'anthropic/claude-3.5-sonnet',
    **kwargs,
) -> InsuranceParser:
    """Factory function to create a configured InsuranceParser.

    Args:
        api_key: OpenRouter API key
        model: Vision model to use
        **kwargs: Additional arguments passed to OpenRouterClient

    Returns:
        Configured InsuranceParser instance
    """
    client = OpenRouterClient(api_key=api_key, model=model, **kwargs)
    return InsuranceParser(client)
