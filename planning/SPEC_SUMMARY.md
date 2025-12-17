# FleetFlow - SPEC Summary

## Quick Reference

| Item | Value |
|------|-------|
| **Project Name** | FleetFlow - Car Rental Management SaaS |
| **Business Model** | Software as a Service (Monthly Subscription) |
| **Technology** | Django 5.x + PostgreSQL + Tailwind CSS + HTMX |
| **Target Market** | Small car rentals (10-50 vehicles) |
| **Pricing** | $99 - $349/month (4 tiers) |
| **Epochs** | 5 (Core, Booking, Advanced, Mobile, Platform) |
| **User Stories** | 34 total (S-001 to S-034) |
| **Tasks (Epoch 1)** | 28 tasks |
| **Wireframes** | 27+ screens |

---

## Subscription Pricing

| Plan | Vehicles | Price | Key Features |
|------|----------|-------|--------------|
| **Starter** | 1-10 | $99/mo | Core features, 1 user |
| **Professional** | 11-25 | $199/mo | + Online booking, 3 users |
| **Business** | 26-50 | $349/mo | + GPS, analytics, 10 users |
| **Enterprise** | 50+ | Custom | Unlimited, dedicated support |

---

## Epoch Overview

### Epoch 1: Core Operations (MVP)
**Goal**: Multi-tenant platform with core rental management

| Story | Description |
|-------|-------------|
| S-027 | Multi-Tenant Architecture |
| S-028 | Tenant Onboarding & Setup |
| S-029 | User Management & Roles |
| S-030 | Plan Limits & Feature Flags |
| S-001 | Vehicle Fleet Management |
| S-002 | Customer Management |
| S-003 | Reservation Calendar System |
| S-004 | Rental Workflow (Check-out/Check-in) |
| S-005 | Basic Contract Generation |
| S-006 | Staff Dashboard |

### Epoch 2: Online Booking & Payments
**Goal**: Customer portal, payments, and subscription billing

| Story | Description |
|-------|-------------|
| S-031 | Stripe Subscription Billing |
| S-032 | Usage Tracking & Overage |
| S-007 | Customer Self-Service Portal |
| S-008 | Online Vehicle Browsing |
| S-009 | Online Reservation Booking |
| S-010 | PayPal Payment Integration |
| S-011 | Electronic Contract Signing |
| S-012 | Customer Notifications |

### Epoch 3: Advanced Features & Integrations
**Goal**: Maintenance, GPS tracking, analytics

| Story | Description |
|-------|-------------|
| S-013 | Maintenance Scheduling System |
| S-014 | GPS Telematics Integration |
| S-015 | Driver License Verification |
| S-016 | Insurance Integration |
| S-017 | Reports and Analytics Dashboard |
| S-018 | Mobile-Optimized Experience |

### Epoch 4: Mobile App with Driver Tracking
**Goal**: Native mobile app for end customers

| Story | Description |
|-------|-------------|
| S-019 | Mobile Customer Authentication |
| S-020 | Mobile Vehicle Browsing & Booking |
| S-021 | My Rentals Dashboard |
| S-022 | Real-Time Vehicle Location Tracking |
| S-023 | Trip Sharing for Safety |
| S-024 | Push Notifications |
| S-025 | Offline Mode & Sync |
| S-026 | Digital Rental Documents |

### Epoch 5: Platform & Growth
**Goal**: Admin tools, API, white-label

| Story | Description |
|-------|-------------|
| S-033 | Super Admin Dashboard |
| S-034 | Public API |
| Future | White-label Options |
| Future | Marketplace for Add-ons |

---

## Key Models (SaaS)

### Tenant (New)
- name, slug (subdomain)
- owner (FK to User)
- plan, stripe_customer_id, stripe_subscription_id
- vehicle_limit, user_limit, features (JSON)
- business_name, address, phone, email, logo
- timezone, currency
- is_active, trial_ends_at

### Vehicle (Tenant-Scoped)
- tenant (FK)
- make, model, year, vin, license_plate
- color, mileage, fuel_type, transmission, seats
- category, features (JSON), daily_rate, weekly_rate, monthly_rate
- status: available, rented, maintenance, retired

### Customer (Tenant-Scoped)
- tenant (FK)
- first_name, last_name, email, phone
- address, city, state, zip_code
- license_number, license_state, license_expiry
- verified, flag (vip/banned/none)

### Reservation (Tenant-Scoped)
- tenant (FK)
- confirmation_number, vehicle (FK), customer (FK)
- pickup_date/time, return_date/time
- daily_rate, subtotal, tax_amount, total_amount
- status: pending, confirmed, in_progress, completed, cancelled

---

## Technology Stack

### Backend
- Django 5.x (Multi-tenant)
- PostgreSQL 15
- Django REST Framework
- Celery + Redis

### Frontend (Web)
- Django Templates
- Tailwind CSS
- HTMX
- Alpine.js

### Mobile (Epoch 4)
- React Native + Expo
- MapBox/Google Maps SDK
- Firebase Cloud Messaging

### Payments & Billing
- Stripe (SaaS subscriptions)
- PayPal (Rental payments)

### Infrastructure
- AWS (ECS, RDS, S3, CloudFront)
- SendGrid / AWS SES (Email)
- Sentry (Monitoring)

---

## Feature Access by Plan

| Feature | Starter | Pro | Business | Enterprise |
|---------|---------|-----|----------|------------|
| Vehicles | 10 | 25 | 50 | Unlimited |
| Users | 1 | 3 | 10 | Unlimited |
| Online Booking | ❌ | ✅ | ✅ | ✅ |
| PayPal Payments | ❌ | ✅ | ✅ | ✅ |
| GPS Tracking | ❌ | ❌ | ✅ | ✅ |
| Analytics | Basic | Standard | Advanced | Custom |
| API Access | ❌ | ❌ | ✅ | ✅ |
| Custom Domain | ❌ | ❌ | ✅ | ✅ |

---

## Revenue Targets

| Metric | Year 1 | Year 2 |
|--------|--------|--------|
| Customers | 50 | 150 |
| MRR | $10,000 | $35,000 |
| ARR | $120,000 | $420,000 |
| Churn | <5%/mo | <3%/mo |

---

## Document Links

### Planning Documents
- [Project Charter](PROJECT_CHARTER.md)
- [User Stories](stories/)
- [Task Documents](tasks/)
- [Wireframes](wireframes/)

### New SaaS Stories
- [S-027 Multi-Tenant Architecture](stories/S-027-multi-tenant-architecture.md)
- [S-028 Tenant Onboarding](stories/S-028-tenant-onboarding.md)
- [S-029 User Management](stories/S-029-user-management.md)
- [S-030 Plan Limits](stories/S-030-plan-limits.md)
- [S-031 Stripe Billing](stories/S-031-stripe-billing.md)
- [S-032 Usage Tracking](stories/S-032-usage-tracking.md)

---

## Development Timeline

| Epoch | Duration | Focus |
|-------|----------|-------|
| 1 | 4 weeks | Multi-tenant MVP |
| 2 | 4 weeks | Payments & billing |
| 3 | 4 weeks | GPS, analytics |
| 4 | 4 weeks | Mobile app |
| 5 | Ongoing | Platform growth |

---

## Approval Status

- [x] SPEC Phase Complete
- [x] Epoch 1 MVP Complete (181 tests, 91% coverage)
- [ ] Epoch 2 Payments Complete
- [ ] Beta Launch (10 customers)
- [ ] Public Launch
- [ ] 50 Paying Customers

---

## Epoch 1 Completion Summary

**Completed: December 2025**

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| Multi-Tenant Architecture (S-027) | Done | 32 | 96% |
| Tenant Onboarding (S-028) | Partial* | - | - |
| User Management (S-029) | Done | - | - |
| Plan Limits (S-030) | Done | - | - |
| Vehicle Fleet (S-001) | Done | 31 | 73-96% |
| Customer Management (S-002) | Done | 27 | 74-97% |
| Reservation Calendar (S-003) | Done | 47 | 97% |
| Rental Workflow (S-004) | Done | - | - |
| Contract Generation (S-005) | Done | 16 | 87-93% |
| Staff Dashboard (S-006) | Done | 28 | 85% |

*Tenant Onboarding partial: Basic tenant creation works, full onboarding wizard planned for Epoch 2.
