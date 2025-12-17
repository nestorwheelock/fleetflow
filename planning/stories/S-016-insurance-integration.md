# S-016: Insurance Integration

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 3 days
**Sprint**: Epoch 3
**Status**: PENDING

## User Story
**As a** rental agent
**I want to** verify customer insurance coverage
**So that** I can ensure vehicles are properly covered

## Acceptance Criteria
- [ ] Can upload insurance card images
- [ ] Can manually enter policy information
- [ ] Optional API verification with insurance provider
- [ ] Track policy expiration dates
- [ ] Alert when customer insurance is expiring
- [ ] Record insurance details for each rental
- [ ] Support for rental insurance purchase option

## Definition of Done
- [ ] Insurance model with policy fields
- [ ] Image upload for insurance cards
- [ ] Manual entry form
- [ ] Expiry tracking and alerts
- [ ] Insurance recorded per reservation
- [ ] Rental insurance options (if offered)
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-068: Insurance model and forms
- T-069: Insurance verification workflow
- T-070: Insurance alerts and expiry tracking

## Notes
- Required fields: Provider, Policy #, Expiry Date
- Optional: Coverage limits, deductible
- Rental insurance options: Basic ($10/day), Premium ($18/day)
- Alert 30 days before expiry
- Decline coverage option with acknowledgment
