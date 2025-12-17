# S-007: Customer Self-Service Portal

**Story Type**: User Story
**Priority**: High
**Estimate**: 5 days
**Sprint**: Epoch 2
**Status**: PENDING

## User Story
**As a** customer
**I want to** create an account and manage my profile online
**So that** I can rent vehicles without calling the office

## Acceptance Criteria
- [ ] Can register with email and password
- [ ] Can verify email address via confirmation link
- [ ] Can update profile information (name, phone, address)
- [ ] Can upload driver's license photo
- [ ] Can view my rental history
- [ ] Can see upcoming reservations
- [ ] Can reset forgotten password
- [ ] Can change password when logged in

## Definition of Done
- [ ] Customer authentication system implemented
- [ ] Registration form with validation
- [ ] Email verification flow working
- [ ] Profile management views
- [ ] Document upload functionality
- [ ] Password reset flow working
- [ ] Rental history page
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-025: Customer authentication system
- T-026: Customer registration flow
- T-027: Profile management views
- T-028: Document upload system
- T-029: Email verification

## Notes
- Use Django allauth or custom auth
- Email verification required before booking
- License must be uploaded and verified before first rental
- Profile completion percentage shown
