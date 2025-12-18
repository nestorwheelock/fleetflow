# S-007: Insurance Card OCR Parsing

**Story Type**: User Story
**Priority**: High
**Estimate**: 3 days
**Sprint**: Sprint 2
**Status**: Pending

## User Story
**As a** rental agent
**I want to** upload an insurance card and have it automatically parsed
**So that** insurance information is captured accurately without manual data entry

## Acceptance Criteria
- [ ] Insurance document upload triggers OCR parsing automatically
- [ ] Loading indicator shown during processing
- [ ] Review modal displays extracted insurance data
- [ ] User can select which fields to apply
- [ ] CustomerInsurance record created with parsed data
- [ ] Multiple insurance records supported per customer
- [ ] Insurance expiration tracking and alerts
- [ ] OCR confidence score displayed
- [ ] Feature only available on Professional plan and above
- [ ] Graceful error handling if parsing fails

## Fields to Extract
- Insurance company name
- Policy number
- Group number (if applicable)
- Effective date
- Expiration date
- Policyholder name
- Policyholder relationship (self, spouse, dependent)
- Coverage type (liability, full coverage, etc.)
- Covered vehicles (year, make, model, VIN)
- Agent name and phone
- NAIC number (if shown)

## Definition of Done
- [ ] CustomerInsurance model created
- [ ] Insurance parser with structured prompts
- [ ] Pydantic schemas for insurance response
- [ ] Parse-insurance API endpoint
- [ ] Apply-insurance-data API endpoint
- [ ] Insurance list/detail views on customer page
- [ ] Insurance upload UI in customer form
- [ ] Plan-based feature gating enforced
- [ ] Unit tests with mocked API responses (>95% coverage)
- [ ] Integration tests for endpoints
- [ ] Documentation updated

## Technical Notes
- Reuses OpenRouter client from S-006
- CustomerInsurance linked to CustomerDocument
- JSON field for covered vehicles array
- Insurance expiration checked on reservation create

## Related Tasks
- T-010: Create automation app and models
- T-012: OpenRouter client and parsers
- T-014: OCR processing endpoints
- T-017: Insurance UI and final integration
