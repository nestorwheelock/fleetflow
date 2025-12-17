# S-031: Stripe Subscription Billing

**Story Type**: User Story
**Priority**: Critical
**Estimate**: 3 days
**Sprint**: Epoch 2
**Status**: Pending

## User Story
**As a** car rental business owner
**I want to** pay for my FleetFlow subscription via Stripe
**So that** I can use the platform with automatic monthly billing

## Acceptance Criteria
- [ ] Can enter credit card via Stripe Elements
- [ ] Can subscribe to any plan (Starter, Pro, Business)
- [ ] Can upgrade/downgrade plan
- [ ] Can view billing history and invoices
- [ ] Can update payment method
- [ ] Can cancel subscription (end of billing period)
- [ ] Receive invoice emails from Stripe
- [ ] Failed payments trigger dunning emails

## Stripe Integration
- [ ] Stripe Customer created on signup
- [ ] Stripe Subscription created on plan selection
- [ ] Webhook handling for subscription events
- [ ] Customer portal for self-service billing
- [ ] Proration on plan changes
- [ ] Grace period for failed payments (7 days)

## Webhook Events to Handle
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.updated`

## Definition of Done
- [ ] Stripe SDK integrated
- [ ] Checkout flow with Stripe Elements
- [ ] Webhook endpoint with signature verification
- [ ] Billing settings page for tenant owners
- [ ] Tests cover billing scenarios (>95% coverage)
- [ ] Documentation for Stripe setup
