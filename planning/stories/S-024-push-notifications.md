# S-024: Push Notifications

**Story Type**: User Story
**Priority**: High
**Estimate**: 4 days
**Sprint**: Epoch 4
**Status**: PENDING

## User Story
**As a** customer
**I want to** receive important notifications on my phone
**So that** I don't miss rental updates

## Acceptance Criteria
- [ ] Receive booking confirmation notification
- [ ] Receive pickup reminder (24 hours before)
- [ ] Receive return reminder (morning of return day)
- [ ] Receive payment success/failure alerts
- [ ] Can manage notification preferences in app
- [ ] Deep links open relevant app screen
- [ ] Notifications work even when app is closed

## Definition of Done
- [ ] Firebase Cloud Messaging setup
- [ ] Push notification service in Django backend
- [ ] Notification types and message templates
- [ ] Deep linking configuration
- [ ] Notification preferences screen
- [ ] Background notification handling
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-109: Firebase Cloud Messaging setup
- T-110: Push notification service in Django
- T-111: Notification types and templates
- T-112: Deep linking configuration
- T-113: Notification preferences screen
- T-114: Background notification handling

## Notes
- FCM for both iOS and Android
- Store device tokens in backend
- Handle token refresh
- Deep link format: fleetflow://rental/123
- Notification categories: Booking, Payment, Reminders
