# S-012: Customer Notifications

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 3 days
**Sprint**: Epoch 2
**Status**: PENDING

## User Story
**As a** customer
**I want to** receive notifications about my rentals
**So that** I stay informed about important updates

## Acceptance Criteria
- [ ] Email confirmation when booking is created
- [ ] Email reminder 24 hours before pickup
- [ ] Email reminder on return day morning
- [ ] Email receipt after vehicle return
- [ ] Email notification if payment fails
- [ ] Can manage notification preferences in settings
- [ ] All emails have consistent branding

## Definition of Done
- [ ] Email notification system using Celery
- [ ] Scheduled reminder tasks (24hr, same-day)
- [ ] Notification preference model
- [ ] Preference management UI
- [ ] Email templates for all notification types
- [ ] Unsubscribe link in emails
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-050: Email notification system
- T-051: Scheduled reminders (Celery)
- T-052: Notification preferences
- T-053: Email templates

## Notes
- Use Django email backend (SMTP or service like SendGrid)
- Celery beat for scheduled tasks
- Templates should be mobile-friendly HTML
- Include unsubscribe option per email type
- Log all sent notifications
