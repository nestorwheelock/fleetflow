# Core OCR library - portable, no Django dependencies

from .client import (
    OpenRouterClient,
    OpenRouterError,
    OpenRouterAPIError,
    OpenRouterAuthError,
    OpenRouterRateLimitError,
    VisionRequest,
    VisionResponse,
)
from .parsers import (
    LicenseParser,
    InsuranceParser,
    create_license_parser,
    create_insurance_parser,
)
from .schemas import (
    LicenseOCRResponse,
    InsuranceOCRResponse,
)

__all__ = [
    # Client
    'OpenRouterClient',
    'OpenRouterError',
    'OpenRouterAPIError',
    'OpenRouterAuthError',
    'OpenRouterRateLimitError',
    'VisionRequest',
    'VisionResponse',
    # Parsers
    'LicenseParser',
    'InsuranceParser',
    'create_license_parser',
    'create_insurance_parser',
    # Schemas
    'LicenseOCRResponse',
    'InsuranceOCRResponse',
]
