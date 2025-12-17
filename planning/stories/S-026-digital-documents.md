# S-026: Digital Rental Documents

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 3 days
**Sprint**: Epoch 4
**Status**: PENDING

## User Story
**As a** customer
**I want to** access all my rental documents in the app
**So that** I have everything I need during my rental

## Acceptance Criteria
- [ ] Can view signed contract in app
- [ ] Can view insurance coverage details
- [ ] Can show rental confirmation to pickup staff
- [ ] Can access emergency contact numbers
- [ ] QR code for quick check-in at pickup counter
- [ ] Can share documents via email or messaging

## Definition of Done
- [ ] Documents tab in app navigation
- [ ] Contract PDF viewer
- [ ] Insurance details screen
- [ ] Rental confirmation with QR code
- [ ] Emergency info screen with tap-to-call
- [ ] Share functionality for documents
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-120: Documents tab with contracts
- T-121: Insurance details screen
- T-122: Rental confirmation with QR code
- T-123: Emergency info screen
- T-124: PDF viewer component

## Notes
- PDF viewer using react-native-pdf
- QR code encodes reservation ID
- Staff app scans QR for quick lookup
- Emergency: Roadside (24/7), Office hours, Police
- Documents screen shows badge for unsigned contracts
