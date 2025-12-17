# S-030: Plan Limits & Feature Flags

**Story Type**: User Story
**Priority**: High
**Estimate**: 2 days
**Sprint**: Epoch 1
**Status**: Pending

## User Story
**As a** FleetFlow platform operator
**I want to** enforce plan limits and feature access
**So that** tenants only use features included in their subscription

## Acceptance Criteria
- [ ] Vehicle count enforced per plan (10, 25, 50, unlimited)
- [ ] User count enforced per plan (1, 3, 10, unlimited)
- [ ] Features enabled/disabled based on plan
- [ ] Graceful messaging when limit reached
- [ ] Upgrade prompts when hitting limits
- [ ] Soft limits with warnings vs hard limits
- [ ] Plan changes take effect immediately

## Plan Limits Matrix

| Limit | Starter | Pro | Business | Enterprise |
|-------|---------|-----|----------|------------|
| Vehicles | 10 | 25 | 50 | Unlimited |
| Users | 1 | 3 | 10 | Unlimited |
| Online Booking | No | Yes | Yes | Yes |
| PayPal Payments | No | Yes | Yes | Yes |
| GPS Tracking | No | No | Yes | Yes |
| Analytics | Basic | Standard | Advanced | Custom |
| API Access | No | No | Yes | Yes |
| Custom Domain | No | No | Yes | Yes |

## Technical Implementation
- [ ] Tenant.features JSONField for feature flags
- [ ] Tenant.vehicle_limit, user_limit fields
- [ ] PlanLimitsMixin for views
- [ ] @feature_required decorator
- [ ] Limit check utilities
- [ ] Upgrade prompt components

## Definition of Done
- [ ] Plan configuration in settings/database
- [ ] Limit checks on create operations
- [ ] Feature flag checks on protected views
- [ ] Upgrade prompts displayed appropriately
- [ ] Tests cover all limit scenarios (>95% coverage)
- [ ] Documentation for plan configuration
