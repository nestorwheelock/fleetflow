"""
Vehicle dashboard analysis parser.

Portability Note: This parser can be used in any vehicle inspection context.
"""
from typing import Type

from ..client import OpenRouterClient
from ..prompts.dashboard import DASHBOARD_ANALYSIS_SYSTEM_PROMPT, DASHBOARD_ANALYSIS_USER_PROMPT
from ..schemas.dashboard import DashboardAnalysisResponse
from .base import BaseDocumentParser


class DashboardParser(BaseDocumentParser[DashboardAnalysisResponse]):
    """Parser for vehicle dashboard analysis from photos.

    Analyzes dashboard photos to extract:
    - Odometer/mileage reading
    - Fuel gauge level
    - Warning light status (check engine, tire pressure, etc.)
    - Other dashboard indicators

    Portability Note: This parser is designed to work with any vehicle
    inspection use case - rental checkout/checkin, fleet management,
    insurance inspections, personal vehicle tracking, etc.
    """

    @property
    def system_prompt(self) -> str:
        return DASHBOARD_ANALYSIS_SYSTEM_PROMPT

    @property
    def user_prompt(self) -> str:
        return DASHBOARD_ANALYSIS_USER_PROMPT

    @property
    def response_model(self) -> Type[DashboardAnalysisResponse]:
        return DashboardAnalysisResponse


def create_dashboard_parser(
    api_key: str,
    model: str = 'anthropic/claude-3.5-sonnet',
    **kwargs,
) -> DashboardParser:
    """Factory function to create a configured DashboardParser.

    Args:
        api_key: OpenRouter API key
        model: Vision model to use
        **kwargs: Additional arguments passed to OpenRouterClient

    Returns:
        Configured DashboardParser instance
    """
    client = OpenRouterClient(api_key=api_key, model=model, **kwargs)
    return DashboardParser(client)
