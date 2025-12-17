# FleetFlow Development Roadmap

## Overview

FleetFlow is a multi-tenant SaaS platform for car rental management. This roadmap outlines the 5 epochs of development, with Epoch 1 complete and Epochs 2-5 planned.

---

## Epoch Summary

| Epoch | Status | Focus | User Stories |
|-------|--------|-------|--------------|
| **1** | Done | Core Operations (MVP) | S-001 to S-006, S-027 to S-030 |
| **2** | Planned | Online Booking & Payments | S-007 to S-012, S-031, S-032 |
| **3** | Planned | Advanced Features | S-013 to S-018 |
| **4** | Planned | Mobile App | S-019 to S-026 |
| **5** | Planned | Platform & Growth | S-033, S-034 |

---

## Epoch 1: Core Operations (MVP) - COMPLETE

**Status**: Done (December 2025)
**Test Coverage**: 181 tests, 91% coverage

### Completed Features

| Story | Description | Status |
|-------|-------------|--------|
| S-027 | Multi-Tenant Architecture | Done |
| S-028 | Tenant Onboarding & Setup | Partial |
| S-029 | User Management & Roles | Done |
| S-030 | Plan Limits & Feature Flags | Done |
| S-001 | Vehicle Fleet Management | Done |
| S-002 | Customer Management | Done |
| S-003 | Reservation Calendar System | Done |
| S-004 | Rental Workflow (Check-out/Check-in) | Done |
| S-005 | Basic Contract Generation | Done |
| S-006 | Staff Dashboard | Done |

### Deliverables

- Multi-tenant Django application
- REST API for all core operations
- Staff dashboard with CRUD operations
- PDF contract generation
- PostgreSQL database with tenant isolation
- Docker Compose development environment
- 91% test coverage

---

## Epoch 2: Online Booking & Payments - PLANNED

**Status**: Not Started
**Focus**: Customer-facing features and monetization

### User Stories

| Story | Description | Priority |
|-------|-------------|----------|
| S-031 | Stripe Subscription Billing | High |
| S-032 | Usage Tracking & Overage | High |
| S-007 | Customer Self-Service Portal | High |
| S-008 | Online Vehicle Browsing | Medium |
| S-009 | Online Reservation Booking | High |
| S-010 | PayPal Payment Integration | Medium |
| S-011 | Electronic Contract Signing | Medium |
| S-012 | Customer Notifications (Email/SMS) | Medium |

### Key Deliverables

- [ ] Stripe integration for SaaS subscriptions
- [ ] Customer-facing booking portal
- [ ] PayPal integration for rental payments
- [ ] E-signature for contracts
- [ ] Email notification system
- [ ] Usage metering and plan limits enforcement

### Technical Requirements

- Stripe SDK integration
- PayPal REST API
- SendGrid/AWS SES for email
- Twilio for SMS (optional)
- Customer authentication (separate from staff)

---

## Epoch 3: Advanced Features & Integrations - PLANNED

**Status**: Not Started
**Focus**: Operational efficiency and data insights

### User Stories

| Story | Description | Priority |
|-------|-------------|----------|
| S-013 | Maintenance Scheduling System | High |
| S-014 | GPS Telematics Integration | Medium |
| S-015 | Driver License Verification | High |
| S-016 | Insurance Integration | Medium |
| S-017 | Reports and Analytics Dashboard | High |
| S-018 | Mobile-Optimized Web Experience | Medium |

### Key Deliverables

- [ ] Maintenance scheduling with reminders
- [ ] GPS tracking integration (OBD-II devices)
- [ ] License verification API integration
- [ ] Insurance provider integration
- [ ] Analytics dashboard with KPIs
- [ ] Responsive mobile web experience

### Technical Requirements

- GPS device API integrations
- License verification API (Checkr, Veriff, etc.)
- Chart.js or similar for analytics
- Celery tasks for scheduled maintenance reminders

---

## Epoch 4: Mobile App with Driver Tracking - PLANNED

**Status**: Not Started
**Focus**: Native mobile experience for customers

### User Stories

| Story | Description | Priority |
|-------|-------------|----------|
| S-019 | Mobile Customer Authentication | High |
| S-020 | Mobile Vehicle Browsing & Booking | High |
| S-021 | My Rentals Dashboard | High |
| S-022 | Real-Time Vehicle Location Tracking | Medium |
| S-023 | Trip Sharing for Safety | Low |
| S-024 | Push Notifications | Medium |
| S-025 | Offline Mode & Sync | Low |
| S-026 | Digital Rental Documents | Medium |

### Key Deliverables

- [ ] React Native mobile app (iOS/Android)
- [ ] Customer mobile authentication
- [ ] In-app vehicle browsing and booking
- [ ] Real-time GPS tracking view
- [ ] Push notifications via Firebase
- [ ] Offline-first architecture

### Technical Requirements

- React Native / Expo
- Firebase Cloud Messaging
- MapBox or Google Maps SDK
- Offline storage (AsyncStorage/SQLite)
- Background location tracking

---

## Epoch 5: Platform & Growth - PLANNED

**Status**: Not Started
**Focus**: Admin tools, API, and scalability

### User Stories

| Story | Description | Priority |
|-------|-------------|----------|
| S-033 | Super Admin Dashboard | High |
| S-034 | Public API | Medium |
| Future | White-label Options | Low |
| Future | Marketplace for Add-ons | Low |

### Key Deliverables

- [ ] Super admin dashboard for managing all tenants
- [ ] Public REST API with documentation
- [ ] API key management and rate limiting
- [ ] White-label branding options
- [ ] Add-on marketplace foundation

### Technical Requirements

- Admin-specific authentication
- API versioning
- OpenAPI/Swagger documentation
- Rate limiting (Redis)
- Multi-branding support

---

## Feature Access by Plan

| Feature | Starter | Professional | Business | Enterprise |
|---------|---------|--------------|----------|------------|
| **Price** | $99/mo | $199/mo | $349/mo | Custom |
| Vehicles | 10 | 25 | 50 | Unlimited |
| Users | 1 | 3 | 10 | Unlimited |
| Online Booking | - | Yes | Yes | Yes |
| PayPal Payments | - | Yes | Yes | Yes |
| GPS Tracking | - | - | Yes | Yes |
| Analytics | Basic | Standard | Advanced | Custom |
| API Access | - | - | Yes | Yes |
| Custom Domain | - | - | Yes | Yes |

---

## Technical Debt & Improvements

### Post-Epoch 1

- [ ] Add authentication views (login/logout templates)
- [ ] Complete tenant onboarding wizard
- [ ] Add password reset flow
- [ ] Implement API rate limiting
- [ ] Add request logging/audit trail
- [ ] Improve error pages (404, 500)

### Performance Optimizations

- [ ] Database query optimization (select_related, prefetch_related)
- [ ] Redis caching for frequently accessed data
- [ ] CDN for static assets
- [ ] Database connection pooling

### Security Enhancements

- [ ] Two-factor authentication
- [ ] Session management improvements
- [ ] CORS configuration for API
- [ ] Security headers (CSP, HSTS)

---

## Development Timeline

| Epoch | Estimated Duration | Prerequisites |
|-------|-------------------|---------------|
| 2 | 4-6 weeks | Epoch 1 complete |
| 3 | 4-6 weeks | Epoch 2 complete |
| 4 | 6-8 weeks | Epoch 3 complete |
| 5 | Ongoing | Epoch 4 complete |

---

## Getting Started

### Current State

```bash
# Clone and run
git clone https://github.com/nestorwheelock/fleetflow.git
cd fleetflow
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# Access
open http://localhost:9199
open http://localhost:9199/admin
```

### Running Tests

```bash
docker compose exec web pytest tests/ -v
docker compose exec web pytest tests/ --cov=apps --cov-report=html
```

---

## Contributing

See the planning documents for detailed specifications:

- [Project Charter](planning/PROJECT_CHARTER.md)
- [SPEC Summary](planning/SPEC_SUMMARY.md)
- [User Stories](planning/stories/)
- [Tasks](planning/tasks/)
- [Wireframes](planning/wireframes/)

---

## Contact

- **GitHub**: https://github.com/nestorwheelock/fleetflow
- **Developer**: https://linuxremotesupport.com
