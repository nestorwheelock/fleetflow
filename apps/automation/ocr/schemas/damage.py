"""
Pydantic schemas for vehicle damage detection responses.

Portability Note: These schemas are pure Python with no Django dependencies.
Can be extracted and used in any vehicle inspection application.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DamageLocation(BaseModel):
    """Location of detected damage on vehicle."""
    zone: str = Field(
        description='Vehicle zone: front, back, driver_side, passenger_side, roof, hood, trunk, interior'
    )
    area: str = Field(
        default='',
        description='Specific area: bumper, fender, door, wheel, windshield, mirror, hood, trunk, seat, dashboard, etc.'
    )
    coordinates: Optional[dict] = Field(
        default=None,
        description='Position in image as percentages {x: 0-100, y: 0-100}'
    )


class DetectedDamage(BaseModel):
    """Single detected damage item."""
    type: str = Field(
        description='Damage type: scratch, dent, crack, chip, stain, tear, missing, rust, other'
    )
    severity: str = Field(
        description='Damage severity: minor, moderate, severe'
    )
    location: DamageLocation = Field(description='Where the damage is located')
    dimensions_estimate: Optional[dict] = Field(
        default=None,
        description='Estimated size: {length_cm: float, width_cm: float, depth_mm: float}'
    )
    description: str = Field(description='Detailed description of the damage')
    confidence: float = Field(
        ge=0.0, le=1.0,
        description='AI confidence in this detection (0.0-1.0)'
    )


class DamageSummary(BaseModel):
    """Summary statistics for detected damages."""
    total_count: int = Field(default=0, description='Total number of damages detected')
    by_type: dict = Field(
        default_factory=dict,
        description='Count by damage type: {scratch: 2, dent: 1}'
    )
    by_severity: dict = Field(
        default_factory=dict,
        description='Count by severity: {minor: 2, moderate: 1}'
    )


class DamageDetectionResponse(BaseModel):
    """Response from AI damage detection analysis.

    Portability Note: This schema can be used for any vehicle inspection,
    not just rentals - personal vehicles, fleet management, insurance, etc.
    """
    damages: list[DetectedDamage] = Field(
        default_factory=list,
        description='List of detected damages'
    )
    overall_condition: str = Field(
        default='unknown',
        description='Overall vehicle condition: excellent, good, fair, poor, damaged'
    )
    summary: DamageSummary = Field(
        default_factory=DamageSummary,
        description='Summary statistics'
    )
    image_quality: str = Field(
        default='unknown',
        description='Image quality assessment: excellent, good, fair, poor'
    )
    notes: str = Field(
        default='',
        description='Additional observations from AI'
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description='Overall confidence in analysis'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'damages': [
                    {
                        'type': 'scratch',
                        'severity': 'minor',
                        'location': {
                            'zone': 'front',
                            'area': 'bumper',
                            'coordinates': {'x': 45, 'y': 80}
                        },
                        'dimensions_estimate': {'length_cm': 6.0, 'width_cm': 0.2},
                        'description': 'Light scratch on front bumper, approximately 6cm long',
                        'confidence': 0.92
                    }
                ],
                'overall_condition': 'good',
                'summary': {
                    'total_count': 1,
                    'by_type': {'scratch': 1},
                    'by_severity': {'minor': 1}
                },
                'image_quality': 'good',
                'notes': 'Vehicle exterior in generally good condition with one minor scratch.',
                'confidence': 0.90
            }
        }
    )
