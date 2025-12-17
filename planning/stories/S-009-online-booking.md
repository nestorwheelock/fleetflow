# S-009: Online Reservation Booking

**Story Type**: User Story
**Priority**: High
**Estimate**: 5 days
**Sprint**: Epoch 2
**Status**: PENDING

## User Story
**As a** customer
**I want to** book a rental online
**So that** I can reserve a vehicle at my convenience

## Acceptance Criteria
- [ ] Can select pickup and return dates/times
- [ ] Can choose from available vehicles for those dates
- [ ] Can add optional extras (GPS, child seat, additional driver)
- [ ] Can see itemized price breakdown before booking
- [ ] Can save reservation as draft to complete later
- [ ] Receive confirmation email after booking
- [ ] Can cancel reservation (with cancellation policy)
- [ ] Can modify reservation dates/vehicle (with policy)

## Definition of Done
- [ ] Multi-step booking flow implemented
- [ ] Date/time picker component
- [ ] Vehicle selection step
- [ ] Add-ons selection step
- [ ] Price calculator (real-time updates)
- [ ] Review and confirm step
- [ ] Confirmation email sent
- [ ] Cancellation/modification logic
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-035: Customer booking flow
- T-036: Date/time picker integration
- T-037: Add-on selection system
- T-038: Price calculator (real-time)
- T-039: Confirmation emails
- T-040: Cancellation/modification logic

## Notes
- Cancellation policy: Full refund 48+ hours, 50% 24-48 hours, no refund <24 hours
- Modification free if 48+ hours before pickup
- Add-ons: GPS ($5/day), Child Seat ($8/day), Additional Driver ($10/day)
- Insurance options presented during booking
