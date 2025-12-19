# S-030: Plan Limits & Feature Flags

**Story Type**: User Story
**Priority**: High
**Estimate**: 2 days
**Sprint**: Epoch 1
**Status**: Partial ✓ (Plan tiers implemented, feature flags pending)

## User Story
**As a** FleetFlow platform operator
**I want to** enforce plan limits and feature access
**So that** tenants only use features included in their subscription

## Acceptance Criteria
- [x] Vehicle count enforced per plan (3, 10, 25, 100, unlimited)
- [x] User count enforced per plan (1, 2, 3, 10, unlimited)
- [x] Per-rental fee model for Personal and Starter plans
- [ ] Features enabled/disabled based on plan
- [ ] Graceful messaging when limit reached
- [ ] Upgrade prompts when hitting limits
- [ ] Soft limits with warnings vs hard limits
- [ ] Plan changes take effect immediately

## Pricing Tiers

| Plan | Base Price | Per Rental Fee | Target Audience |
|------|------------|----------------|-----------------|
| Personal | Free | $2.50 | Individuals with 1-3 cars |
| Starter | $29/mo | $0.75 | Small rental shops |
| Professional | $79/mo | None | Growing businesses |
| Business | $199/mo | None | Established companies |
| Enterprise | Custom | None | Large fleets |

## Plan Limits Matrix

| Limit | Personal | Starter | Pro | Business | Enterprise |
|-------|----------|---------|-----|----------|------------|
| Vehicles | 3 | 10 | 25 | 100 | Unlimited |
| Users | 1 | 2 | 3 | 10 | Unlimited |
| Online Booking | No | No | Yes | Yes | Yes |
| Customer Portal | No | No | Yes | Yes | Yes |
| GPS Tracking | No | No | No | Yes | Yes |
| Analytics | None | Basic | Standard | Advanced | Custom |
| API Access | No | No | No | Yes | Yes |
| Custom Domain | No | No | No | Yes | Yes |
| FleetFlow Branding | Required | Required | Optional | None | None |

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
