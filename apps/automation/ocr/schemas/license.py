from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LicenseAddress(BaseModel):
    street: str = Field(default='', description='Street address')
    city: str = Field(default='', description='City')
    state: str = Field(default='', description='State/Province')
    zip_code: str = Field(default='', description='ZIP/Postal code')
    country: str = Field(default='USA', description='Country')


class LicenseOCRResponse(BaseModel):
    """Structured response from driver's license OCR parsing."""

    country: str = Field(default='USA', description='Issuing country')
    issuing_authority: str = Field(default='', description='Issuing state/authority')

    license_number: str = Field(default='', description='Driver license number')
    license_class: str = Field(default='', description='License class (A, B, C, CDL, etc.)')
    issue_date: Optional[date] = Field(default=None, description='License issue date')
    expiration_date: Optional[date] = Field(default=None, description='License expiration date')

    first_name: str = Field(default='', description='First name')
    middle_name: str = Field(default='', description='Middle name')
    last_name: str = Field(default='', description='Last name')
    date_of_birth: Optional[date] = Field(default=None, description='Date of birth')

    address: LicenseAddress = Field(default_factory=LicenseAddress, description='Address')

    gender: str = Field(default='', description='Gender (M/F/X)')
    height: str = Field(default='', description="Height (e.g., 5'10\" or 178cm)")
    weight: str = Field(default='', description='Weight (e.g., 180 lbs or 82kg)')
    eye_color: str = Field(default='', description='Eye color')
    hair_color: str = Field(default='', description='Hair color')

    restrictions: str = Field(default='', description='License restrictions')
    endorsements: str = Field(default='', description='License endorsements')
    donor_status: Optional[bool] = Field(default=None, description='Organ donor status')

    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description='OCR confidence score')
    raw_text: str = Field(default='', description='Raw extracted text for debugging')

    has_photo: bool = Field(default=False, description='Whether a photo was detected')
    photo_region: Optional[dict] = Field(
        default=None,
        description='Photo region coordinates {x, y, width, height} as percentages'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'country': 'USA',
                'issuing_authority': 'Texas',
                'license_number': 'DL12345678',
                'license_class': 'C',
                'issue_date': '2020-01-15',
                'expiration_date': '2028-01-15',
                'first_name': 'John',
                'middle_name': 'Robert',
                'last_name': 'Doe',
                'date_of_birth': '1985-05-15',
                'address': {
                    'street': '123 Main St',
                    'city': 'Austin',
                    'state': 'TX',
                    'zip_code': '78701',
                    'country': 'USA'
                },
                'gender': 'M',
                'height': "5'10\"",
                'weight': '180 lbs',
                'eye_color': 'BRN',
                'hair_color': 'BLK',
                'restrictions': 'Corrective Lenses',
                'endorsements': 'Motorcycle',
                'donor_status': True,
                'confidence': 0.95,
                'has_photo': True
            }
        }
    )
