# S-004: Rental Workflow (Check-out/Check-in)

**Story Type**: User Story
**Priority**: High
**Estimate**: 4 days
**Sprint**: Epoch 1
**Status**: PENDING

## User Story
**As a** rental agent
**I want to** process vehicle pickups and returns
**So that** I can track the complete rental lifecycle

## Acceptance Criteria
- [ ] Can check out vehicle with odometer reading
- [ ] Can record pre-rental vehicle condition (exterior/interior)
- [ ] Can upload condition photos at checkout
- [ ] Can check in vehicle with return odometer reading
- [ ] Can record post-rental condition and note damages
- [ ] Can calculate final charges (extra miles, fuel, damages)
- [ ] Can generate receipt with all charges
- [ ] Vehicle status updates automatically through workflow

## Definition of Done
- [ ] Check-out workflow with multi-step form
- [ ] Check-in workflow with damage recording
- [ ] Condition report model with photo support
- [ ] Mileage tracking and overage calculation
- [ ] Fuel level recording and charges
- [ ] Damage assessment and additional charges
- [ ] Receipt generation
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-015: Check-out workflow and forms
- T-016: Check-in workflow and forms
- T-017: Condition report model
- T-018: Charge calculation logic

## Notes
- Mileage limit: configurable per vehicle (default 150 mi/day)
- Overage rate: $0.25/mile
- Fuel policy: Return same level or pay $4.50/gallon
- Late fee: $15/hour up to 3 hours, then full day rate
