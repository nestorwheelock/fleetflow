"""
Pydantic schemas for vehicle damage comparison responses.

Portability Note: These schemas are pure Python with no Django dependencies.
Can be extracted and used in any vehicle inspection application.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ComparedDamage(BaseModel):
    """Damage item identified in comparison analysis."""
    type: str = Field(
        description='Damage type: scratch, dent, crack, chip, stain, tear, missing, rust, other'
    )
    severity: str = Field(
        description='Damage severity: minor, moderate, severe'
    )
    location: dict = Field(
        description='Where the damage is located: {zone: str, area: str}'
    )
    description: str = Field(description='Detailed description of the damage')
    confidence: float = Field(
        ge=0.0, le=1.0,
        description='AI confidence in this detection'
    )
    estimated_repair_cost: Optional[float] = Field(
        default=None,
        description='Estimated repair cost in USD (if determinable)'
    )


class DamageComparisonResponse(BaseModel):
    """Response from AI damage comparison analysis.

    Compares two photos (before/after, checkout/checkin) of the same vehicle
    area to identify new damage that occurred during the rental period.

    Portability Note: This schema can be used for any before/after vehicle
    comparison - rentals, fleet returns, accident assessment, etc.
    """
    new_damages: list[ComparedDamage] = Field(
        default_factory=list,
        description='New damages detected in the "after" image that were not in "before"'
    )
    pre_existing_count: int = Field(
        default=0,
        description='Number of pre-existing damages matched between images'
    )
    resolved_count: int = Field(
        default=0,
        description='Number of damages visible in "before" but not in "after" (repaired)'
    )
    comparison_quality: str = Field(
        default='unknown',
        description='Quality of comparison: excellent, good, fair, poor'
    )
    angle_match: str = Field(
        default='unknown',
        description='How well the photo angles match: excellent, good, fair, poor'
    )
    lighting_difference: str = Field(
        default='similar',
        description='Lighting difference between photos: similar, moderate, significant'
    )
    summary: str = Field(
        default='',
        description='Natural language summary of comparison findings'
    )
    total_new_damage_count: int = Field(
        default=0,
        description='Total count of new damages detected'
    )
    estimated_total_repair_cost: Optional[float] = Field(
        default=None,
        description='Total estimated repair cost for all new damages'
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description='Overall confidence in comparison analysis'
    )
    notes: str = Field(
        default='',
        description='Additional observations about the comparison'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'new_damages': [
                    {
                        'type': 'dent',
                        'severity': 'moderate',
                        'location': {'zone': 'driver_side', 'area': 'door'},
                        'description': 'New dent on driver side door, approximately 5cm diameter',
                        'confidence': 0.88,
                        'estimated_repair_cost': 250.00
                    },
                    {
                        'type': 'scratch',
                        'severity': 'minor',
                        'location': {'zone': 'back', 'area': 'bumper'},
                        'description': 'Light scratch on rear bumper, not present in checkout photo',
                        'confidence': 0.82,
                        'estimated_repair_cost': 100.00
                    }
                ],
                'pre_existing_count': 1,
                'resolved_count': 0,
                'comparison_quality': 'good',
                'angle_match': 'good',
                'lighting_difference': 'moderate',
                'summary': '2 new damages detected during rental period. Driver side door has '
                           'a moderate dent and rear bumper has a minor scratch. Pre-existing '
                           'scratch on front bumper remains unchanged.',
                'total_new_damage_count': 2,
                'estimated_total_repair_cost': 350.00,
                'confidence': 0.85,
                'notes': 'Comparison affected slightly by different lighting conditions.'
            }
        }
    )
