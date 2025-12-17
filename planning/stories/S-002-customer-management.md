# S-002: Customer Management

**Story Type**: User Story
**Priority**: High
**Estimate**: 4 days
**Sprint**: Epoch 1
**Status**: PENDING

## User Story
**As a** rental agent
**I want to** manage customer information
**So that** I can track renters, their documents, and rental history

## Acceptance Criteria
- [ ] Can add customers with contact info (name, email, phone, address)
- [ ] Can record driver's license details (number, state, expiry, DOB)
- [ ] Can upload license photos and other documents
- [ ] Can view customer rental history
- [ ] Can search customers by name, email, phone, or license number
- [ ] Can flag customers (VIP, regular, banned)
- [ ] Can add notes to customer profiles
- [ ] Can see total rentals and lifetime value

## Definition of Done
- [ ] Customer model created with all required fields
- [ ] Document upload model for license/insurance
- [ ] Customer CRUD views implemented
- [ ] Search functionality working
- [ ] Rental history displayed on customer profile
- [ ] Customer flags/tags system working
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-006: Customer model and migrations
- T-007: Customer admin interface
- T-008: Customer CRUD views
- T-009: Document upload for customers

## Notes
- License expiry alert when within 30 days
- Support for international licenses
- Customer flags: VIP, Regular, New, Banned, Blacklisted
