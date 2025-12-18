"""
Pydantic schemas for vehicle dashboard analysis responses.

Portability Note: These schemas are pure Python with no Django dependencies.
Can be extracted and used in any vehicle inspection application.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OdometerReading(BaseModel):
    """Odometer/mileage reading from dashboard."""
    reading: int = Field(description='Mileage reading as integer')
    unit: str = Field(default='miles', description='Unit: miles or kilometers')
    display_type: str = Field(default='digital', description='Display type: digital or analog')
    confidence: float = Field(
        ge=0.0, le=1.0,
        description='Confidence in the reading (0.0-1.0)'
    )
    raw_reading: str = Field(
        default='',
        description='Exactly what was visible on the odometer'
    )


class FuelGaugeReading(BaseModel):
    """Fuel gauge reading from dashboard."""
    level: str = Field(
        description='Fuel level: empty, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, full'
    )
    percentage: int = Field(
        default=0, ge=0, le=100,
        description='Estimated fuel percentage (0-100)'
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description='Confidence in the reading'
    )


class WarningLight(BaseModel):
    """Individual warning light/indicator status."""
    indicator: str = Field(
        description='Indicator name: check_engine, oil_pressure, battery, temperature, '
                    'tire_pressure, abs, airbag, brake, service_due, door_ajar, '
                    'trunk_open, seatbelt, low_fuel, washer_fluid, headlight_out, etc.'
    )
    status: str = Field(description='Status: on, off, blinking, unknown')
    color: str = Field(default='', description='Light color: red, amber, yellow, green, blue')
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description='Confidence in detection'
    )


class OtherIndicator(BaseModel):
    """Other dashboard indicator or message."""
    indicator: str = Field(description='Indicator name or type')
    status: str = Field(description='Current status')
    description: str = Field(default='', description='Additional details')


class DashboardAnalysisResponse(BaseModel):
    """Response from AI dashboard analysis.

    Extracts mileage, fuel level, and warning light status from dashboard photos.

    Portability Note: This schema can be used for any vehicle inspection,
    not just rentals - personal vehicles, fleet management, insurance, etc.
    """
    odometer: Optional[OdometerReading] = Field(
        default=None,
        description='Odometer/mileage reading'
    )
    fuel_gauge: Optional[FuelGaugeReading] = Field(
        default=None,
        description='Fuel gauge reading'
    )
    warning_lights: list[WarningLight] = Field(
        default_factory=list,
        description='Detected warning lights and their status'
    )
    other_indicators: list[OtherIndicator] = Field(
        default_factory=list,
        description='Other dashboard indicators or messages'
    )
    image_quality: str = Field(
        default='unknown',
        description='Image quality: excellent, good, fair, poor'
    )
    notes: str = Field(
        default='',
        description='Additional observations'
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description='Overall confidence in analysis'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'odometer': {
                    'reading': 45234,
                    'unit': 'miles',
                    'display_type': 'digital',
                    'confidence': 0.98,
                    'raw_reading': '045234'
                },
                'fuel_gauge': {
                    'level': '3/4',
                    'percentage': 75,
                    'confidence': 0.85
                },
                'warning_lights': [
                    {
                        'indicator': 'check_engine',
                        'status': 'off',
                        'color': '',
                        'confidence': 0.95
                    },
                    {
                        'indicator': 'tire_pressure',
                        'status': 'on',
                        'color': 'amber',
                        'confidence': 0.92
                    }
                ],
                'other_indicators': [
                    {
                        'indicator': 'service_due',
                        'status': 'on',
                        'description': 'Service reminder light illuminated'
                    }
                ],
                'image_quality': 'good',
                'notes': 'Dashboard clearly visible. TPMS warning light is on.',
                'confidence': 0.90
            }
        }
    )
