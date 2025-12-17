# S-032: Usage Tracking & Overage

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 2 days
**Sprint**: Epoch 2
**Status**: Pending

## User Story
**As a** FleetFlow platform operator
**I want to** track tenant usage metrics
**So that** I can enforce limits and identify upgrade opportunities

## Acceptance Criteria
- [ ] Track vehicle count per tenant
- [ ] Track user count per tenant
- [ ] Track reservation count per month
- [ ] Track storage usage per tenant
- [ ] Dashboard shows usage vs limits
- [ ] Alerts when approaching limits (80%, 90%)
- [ ] Usage history for billing disputes

## Usage Metrics to Track

| Metric | Purpose |
|--------|---------|
| Vehicles | Plan limit enforcement |
| Users | Plan limit enforcement |
| Reservations/month | Analytics, upsell |
| Storage (MB) | Future billing |
| API calls/month | Enterprise metering |
| Active rentals | Usage patterns |

## Technical Implementation
- [ ] UsageMetric model with daily snapshots
- [ ] Celery task for daily usage calculation
- [ ] Usage dashboard widget
- [ ] Threshold alert system
- [ ] Usage API for admin dashboard

## Definition of Done
- [ ] Usage tracking models created
- [ ] Daily usage snapshot task
- [ ] Usage displayed in tenant settings
- [ ] Alert emails at 80%, 90%, 100% limits
- [ ] Tests cover usage tracking (>95% coverage)
- [ ] Documentation for usage system
