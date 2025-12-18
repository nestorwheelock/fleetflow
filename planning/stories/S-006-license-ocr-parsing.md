# S-006: Driver's License OCR Parsing

**Story Type**: User Story
**Priority**: High
**Estimate**: 4 days
**Sprint**: Sprint 2
**Status**: Pending

## User Story
**As a** rental agent
**I want to** upload a driver's license front and have it automatically parsed
**So that** customer data is auto-filled and I save time on data entry

## Acceptance Criteria
- [ ] When license image uploaded, OCR parsing triggers automatically
- [ ] Loading indicator shown during processing
- [ ] Review modal displays extracted data for user approval
- [ ] User can select which fields to apply (checkbox per field)
- [ ] Only empty fields are auto-filled (existing data not overwritten)
- [ ] Profile photo extracted from license and set as customer photo
- [ ] OCR confidence score displayed to user
- [ ] Feature only available on Professional plan and above
- [ ] Graceful error handling if parsing fails

## Fields to Extract
- Country and issuing authority (state)
- License number, class, issue date, expiration date
- Name (first, middle, last)
- Date of birth
- Address (street, city, state, zip)
- Gender
- Height, weight
- Eye color, hair color
- Restrictions and endorsements
- Donor status (if indicated)
- Photo (for profile photo)

## Definition of Done
- [ ] Customer model extended with new license fields
- [ ] Profile photo field added to Customer model
- [ ] OpenRouter client implemented with vision API support
- [ ] License parser with structured prompts
- [ ] Pydantic schemas for response validation
- [ ] Photo extraction utility
- [ ] Parse-license API endpoint
- [ ] Apply-license-data API endpoint
- [ ] OCR status polling endpoint
- [ ] Alpine.js review modal component
- [ ] Plan-based feature gating enforced
- [ ] Unit tests with mocked API responses (>95% coverage)
- [ ] Integration tests for endpoints
- [ ] Documentation updated

## Technical Notes
- Uses OpenRouter API with vision-capable models
- Async processing via Celery tasks
- Portable OCR module design (no Django deps in core)
- Rate limiting: 10 requests/hour per user

## Related Tasks
- T-010: Create automation app and models
- T-012: OpenRouter client and parsers
- T-014: OCR processing endpoints
- T-016: Customer form OCR integration
