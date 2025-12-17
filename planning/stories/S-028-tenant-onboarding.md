# S-028: Tenant Onboarding & Setup

**Story Type**: User Story
**Priority**: Critical
**Estimate**: 2 days
**Sprint**: Epoch 1
**Status**: Pending

## User Story
**As a** car rental business owner
**I want to** sign up and set up my rental business on FleetFlow
**So that** I can start managing my fleet without technical setup

## Acceptance Criteria
- [ ] Can sign up with email and password
- [ ] Can choose a subdomain (company-name.fleetflow.io)
- [ ] Can enter business information (name, address, phone, email)
- [ ] Can upload company logo
- [ ] Can select subscription plan (Starter, Pro, Business)
- [ ] 14-day free trial automatically activated
- [ ] Receive welcome email with getting started guide
- [ ] Guided setup wizard for first vehicle and customer

## User Flow
1. Visit fleetflow.io/signup
2. Enter email, password, business name
3. Choose subdomain (check availability)
4. Select subscription plan
5. Enter business details
6. Upload logo (optional)
7. Start free trial
8. Redirected to setup wizard

## Definition of Done
- [ ] Signup form with validation
- [ ] Subdomain availability checker (AJAX)
- [ ] Tenant created with trial status
- [ ] Owner user account created
- [ ] Welcome email sent via SendGrid/SES
- [ ] Setup wizard guides through first steps
- [ ] Tests cover signup flow (>95% coverage)
- [ ] Documentation for onboarding process
