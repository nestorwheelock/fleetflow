from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CoveredVehicle(BaseModel):
    """Vehicle covered under the insurance policy."""
    year: Optional[int] = Field(default=None, description='Vehicle year')
    make: str = Field(default='', description='Vehicle make')
    model: str = Field(default='', description='Vehicle model')
    vin: str = Field(default='', description='Vehicle Identification Number')


class InsuranceOCRResponse(BaseModel):
    """Structured response from insurance card OCR parsing."""

    company_name: str = Field(default='', description='Insurance company name')
    policy_number: str = Field(default='', description='Policy number')
    group_number: str = Field(default='', description='Group number')

    effective_date: Optional[date] = Field(default=None, description='Coverage effective date')
    expiration_date: Optional[date] = Field(default=None, description='Coverage expiration date')

    policyholder_name: str = Field(default='', description='Name of policyholder')
    policyholder_relationship: str = Field(
        default='',
        description='Relationship to insured (self, spouse, dependent)'
    )

    coverage_type: str = Field(
        default='',
        description='Type of coverage (liability, collision, comprehensive, full)'
    )
    liability_limits: str = Field(
        default='',
        description='Liability coverage limits (e.g., 100/300/100)'
    )

    covered_vehicles: List[CoveredVehicle] = Field(
        default_factory=list,
        description='List of vehicles covered'
    )

    agent_name: str = Field(default='', description='Insurance agent name')
    agent_phone: str = Field(default='', description='Insurance agent phone')
    company_phone: str = Field(default='', description='Insurance company claims phone')

    naic_number: str = Field(default='', description='NAIC company code')
    state: str = Field(default='', description='State where policy is issued')

    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description='OCR confidence score')
    raw_text: str = Field(default='', description='Raw extracted text for debugging')

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'company_name': 'State Farm',
                'policy_number': 'SF123456789',
                'group_number': 'GRP001',
                'effective_date': '2024-01-01',
                'expiration_date': '2025-01-01',
                'policyholder_name': 'John Doe',
                'policyholder_relationship': 'self',
                'coverage_type': 'full',
                'liability_limits': '100/300/100',
                'covered_vehicles': [
                    {
                        'year': 2023,
                        'make': 'Toyota',
                        'model': 'Camry',
                        'vin': '1HGBH41JXMN109186'
                    }
                ],
                'agent_name': 'Jane Smith',
                'agent_phone': '555-0100',
                'company_phone': '1-800-STATE-FARM',
                'confidence': 0.92
            }
        }
    )
