from .license import LicenseOCRResponse, LicenseAddress
from .insurance import InsuranceOCRResponse, CoveredVehicle
from .damage import (
    DamageDetectionResponse,
    DetectedDamage,
    DamageLocation,
    DamageSummary,
)
from .dashboard import (
    DashboardAnalysisResponse,
    OdometerReading,
    FuelGaugeReading,
    WarningLight,
    OtherIndicator,
)
from .comparison import (
    DamageComparisonResponse,
    ComparedDamage,
)

__all__ = [
    'LicenseOCRResponse',
    'LicenseAddress',
    'InsuranceOCRResponse',
    'CoveredVehicle',
    'DamageDetectionResponse',
    'DetectedDamage',
    'DamageLocation',
    'DamageSummary',
    'DashboardAnalysisResponse',
    'OdometerReading',
    'FuelGaugeReading',
    'WarningLight',
    'OtherIndicator',
    'DamageComparisonResponse',
    'ComparedDamage',
]
