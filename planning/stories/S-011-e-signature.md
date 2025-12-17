# S-011: Electronic Contract Signing

**Story Type**: User Story
**Priority**: High
**Estimate**: 3 days
**Sprint**: Epoch 2
**Status**: PENDING

## User Story
**As a** customer
**I want to** sign the rental contract electronically
**So that** I can complete paperwork before pickup

## Acceptance Criteria
- [ ] Can view contract terms online before signing
- [ ] Can provide electronic signature (draw or type)
- [ ] Signature timestamp and IP address recorded
- [ ] Signed contract stored as PDF with embedded signature
- [ ] Signed contract emailed to customer
- [ ] Staff can verify signature status on reservation
- [ ] Cannot proceed with pickup without signed contract

## Definition of Done
- [ ] E-signature capture UI (canvas drawing)
- [ ] Type-to-sign option
- [ ] Signature data storage (base64 image)
- [ ] Timestamp and IP recording
- [ ] PDF generation with embedded signature
- [ ] Email delivery of signed contract
- [ ] Signature verification on staff side
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-046: E-signature capture UI
- T-047: Signature verification and storage
- T-048: PDF generation with signature
- T-049: Contract email delivery

## Notes
- Use Signature Pad JS library for drawing
- Typed signatures use cursive font
- Legal disclaimer about electronic signatures
- Contract must be signed within 24 hours of booking
- Unsigned contracts send reminder emails
