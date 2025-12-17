# FleetFlow - Project Charter

## Project Overview

**Project Name**: FleetFlow - Car Rental Management SaaS
**Version**: 1.0.0
**Business Model**: Software as a Service (SaaS)
**Target Market**: Small to medium car rental businesses (10-50 vehicles)

---

## Executive Summary

FleetFlow is a multi-tenant SaaS platform for car rental management, designed specifically for local and regional rental businesses. The platform provides end-to-end rental operations including fleet management, reservations, online booking, payments, contracts, maintenance tracking, and GPS fleet tracking.

**Business Model**: Monthly subscription ($99-499/month based on fleet size and features)

---

## Business Objectives

### Primary Goals
1. **Build recurring revenue** — Monthly subscriptions from rental businesses
2. **Capture underserved market** — Small rentals ignored by enterprise vendors
3. **Reduce customer acquisition cost** — Self-service signups, free trial
4. **Achieve profitability** — 100+ paying customers within 12 months
5. **Create sellable asset** — Build toward acquisition at 3-5x ARR

### Success Metrics

| Metric | Year 1 Target | Year 2 Target |
|--------|---------------|---------------|
| Paying Customers | 50 | 150 |
| Monthly Recurring Revenue (MRR) | $10,000 | $35,000 |
| Annual Recurring Revenue (ARR) | $120,000 | $420,000 |
| Churn Rate | <5%/month | <3%/month |
| Customer Acquisition Cost | <$200 | <$150 |
| Lifetime Value (LTV) | >$2,000 | >$3,000 |

---

## Revenue Model

### Subscription Tiers

| Plan | Vehicles | Monthly Price | Annual Price | Features |
|------|----------|---------------|--------------|----------|
| **Starter** | 1-10 | $99 | $990 (17% off) | Core features, 1 user |
| **Professional** | 11-25 | $199 | $1,990 (17% off) | + Online booking, 3 users |
| **Business** | 26-50 | $349 | $3,490 (17% off) | + GPS, analytics, 10 users |
| **Enterprise** | 50+ | Custom | Custom | Unlimited, dedicated support |

### Revenue Projections

| Scenario | Customers | Avg MRR | Monthly Revenue | Annual Revenue |
|----------|-----------|---------|-----------------|----------------|
| Conservative | 50 | $175 | $8,750 | $105,000 |
| Target | 100 | $200 | $20,000 | $240,000 |
| Optimistic | 200 | $225 | $45,000 | $540,000 |

### Unit Economics

| Metric | Value |
|--------|-------|
| Average Revenue Per User (ARPU) | $200/month |
| Customer Acquisition Cost (CAC) | $150 |
| Lifetime Value (LTV) | $2,400 (12-month avg retention) |
| LTV:CAC Ratio | 16:1 |
| Gross Margin | 80% |
| Payback Period | <1 month |

---

## Scope

### Platform Features (5 Epochs)

**Epoch 1: Core Operations (MVP)**
- Multi-tenant architecture
- Tenant onboarding and setup
- Vehicle fleet management
- Customer database
- Reservation calendar with conflict prevention
- Check-out/check-in workflows
- PDF contract generation
- Staff dashboard

**Epoch 2: Online Booking & Payments**
- Customer self-service portal
- Online vehicle browsing
- Self-service booking
- PayPal payment processing (for rentals)
- E-signature contracts
- Email notifications
- Stripe subscription billing (for SaaS)

**Epoch 3: Advanced Features**
- Maintenance scheduling
- GPS/telematics integration
- License verification API
- Analytics dashboard
- Usage tracking and limits

**Epoch 4: Mobile App**
- React Native mobile app
- Real-time vehicle tracking
- Trip sharing
- Push notifications
- Offline mode

**Epoch 5: Platform & Growth** *(Future)*
- Admin super-dashboard (manage all tenants)
- White-label options
- Public API
- Marketplace for add-ons
- Affiliate/referral system

### Out of Scope (Future)
- Multi-location per tenant
- Franchise management
- Vehicle auction/sales module
- Full accounting/ERP integration
- Digital key/keyless entry

---

## Technical Architecture

### Multi-Tenant Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEETFLOW SAAS ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│   │Tenant A │  │Tenant B │  │Tenant C │  │Tenant N │          │
│   │(Rental  │  │(Rental  │  │(Rental  │  │  ...    │          │
│   │ Co. 1)  │  │ Co. 2)  │  │ Co. 3)  │  │         │          │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │
│        │            │            │            │                │
│        └────────────┼────────────┼────────────┘                │
│                     │            │                             │
│              ┌──────▼────────────▼──────┐                      │
│              │     FLEETFLOW PLATFORM    │                      │
│              │    (Shared Application)   │                      │
│              └──────────────┬───────────┘                      │
│                             │                                   │
│    ┌────────────────────────┼────────────────────────┐         │
│    │                        │                        │         │
│  ┌─▼───────┐         ┌──────▼──────┐          ┌─────▼─────┐   │
│  │ Tenant  │         │   Shared    │          │  Billing  │   │
│  │ Data    │         │  Services   │          │  Service  │   │
│  │(Isolated)│         │             │          │ (Stripe)  │   │
│  └─────────┘         └─────────────┘          └───────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    INFRASTRUCTURE                        │   │
│  │  PostgreSQL │ Redis │ S3 │ Celery │ AWS                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Tenant Isolation Strategy

| Component | Isolation Method |
|-----------|------------------|
| Database | Shared database, tenant_id on all tables |
| File Storage | Separate S3 prefixes per tenant |
| Subdomains | tenant-name.yourdomain.com |
| API | Tenant identified via JWT token |
| Caching | Redis key prefixes per tenant |

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.x, Python 3.12+ |
| Database | PostgreSQL 15 (multi-tenant) |
| Cache | Redis |
| Task Queue | Celery |
| API | Django REST Framework |
| Frontend | Django Templates, Tailwind CSS, HTMX, Alpine.js |
| Mobile | React Native, Expo |
| SaaS Billing | Stripe (subscriptions) |
| Rental Payments | PayPal |
| Hosting | AWS (ECS, RDS, S3, CloudFront) |
| Monitoring | Sentry, CloudWatch |
| Email | SendGrid / AWS SES |

---

## Data Model (Multi-Tenant)

### Core Tenant Model

```python
class Tenant(models.Model):
    # Identity
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # subdomain
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # Subscription (Stripe)
    plan = models.CharField(choices=PLAN_CHOICES)
    stripe_customer_id = models.CharField()
    stripe_subscription_id = models.CharField()
    subscription_status = models.CharField()  # active, past_due, canceled

    # Plan Limits
    vehicle_limit = models.IntegerField()
    user_limit = models.IntegerField()
    features = models.JSONField()  # enabled features

    # Business Info
    business_name = models.CharField()
    business_address = models.TextField()
    business_phone = models.CharField()
    business_email = models.EmailField()
    logo = models.ImageField()
    timezone = models.CharField()
    currency = models.CharField(default='USD')

    # Status
    is_active = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Tenant-Scoped Models

All business models include tenant foreign key:

```python
class TenantModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Vehicle(TenantModel):
    # ... vehicle fields

class Customer(TenantModel):
    # ... customer fields

class Reservation(TenantModel):
    # ... reservation fields
```

---

## Feature Access by Plan

| Feature | Starter | Professional | Business | Enterprise |
|---------|---------|--------------|----------|------------|
| **Price** | $99/mo | $199/mo | $349/mo | Custom |
| **Vehicles** | 10 | 25 | 50 | Unlimited |
| **Users** | 1 | 3 | 10 | Unlimited |
| **Reservations** | Unlimited | Unlimited | Unlimited | Unlimited |
| **Customers** | Unlimited | Unlimited | Unlimited | Unlimited |
| **Online Booking** | ❌ | ✅ | ✅ | ✅ |
| **PayPal Payments** | ❌ | ✅ | ✅ | ✅ |
| **E-Signatures** | ❌ | ✅ | ✅ | ✅ |
| **GPS Tracking** | ❌ | ❌ | ✅ | ✅ |
| **Analytics** | Basic | Standard | Advanced | Custom |
| **API Access** | ❌ | ❌ | ✅ | ✅ |
| **Support** | Email | Priority | Phone | Dedicated |
| **Custom Domain** | ❌ | ❌ | ✅ | ✅ |
| **White Label** | ❌ | ❌ | ❌ | ✅ |

---

## Go-To-Market Strategy

### Target Customer Profile
- Small car rental businesses (10-50 vehicles)
- Currently using spreadsheets or outdated software
- US-based (initial market)
- Revenue: $100K - $2M/year
- Pain: Manual processes, no online booking, double-bookings

### Acquisition Channels
1. **SEO/Content** — "car rental software", "fleet management small business"
2. **Google Ads** — Target rental business keywords
3. **Industry Forums** — Car rental association communities
4. **Direct Outreach** — LinkedIn, cold email
5. **Referral Program** — 1 month free per referral

### Conversion Funnel
```
Landing Page → Free Trial (14 days) → Onboarding → Paid Subscription
     ↓              ↓                    ↓              ↓
   100%            20%                  60%            70%
              (of visitors)      (of trial starts) (of onboarded)
```

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low initial adoption | High | Medium | Free trial, content marketing |
| High churn | High | Medium | Onboarding support, feature stickiness |
| Competition | Medium | Low | Focus on SMB, better UX, lower price |
| Scaling issues | Medium | Low | Cloud-native architecture |
| Security breach | High | Low | SOC 2 compliance, encryption |
| Payment failures | Medium | Medium | Dunning emails, grace period |

---

## Development Roadmap

| Epoch | Focus | Duration | Key Deliverables |
|-------|-------|----------|------------------|
| 1 | MVP | 4 weeks | Multi-tenant core, fleet, reservations |
| 2 | Monetization | 4 weeks | Online booking, payments, Stripe billing |
| 3 | Stickiness | 4 weeks | GPS, maintenance, analytics |
| 4 | Mobile | 4 weeks | iOS/Android app |
| 5 | Scale | Ongoing | Admin tools, API, white-label |

---

## Success Criteria

### MVP Launch (Epoch 1-2)
- [ ] Multi-tenant architecture working
- [ ] 10 beta customers onboarded
- [ ] Stripe billing integrated
- [ ] 99% uptime achieved

### Product-Market Fit (Month 6)
- [ ] 50 paying customers
- [ ] <5% monthly churn
- [ ] LTV > 3x CAC
- [ ] NPS score > 40

### Growth Phase (Month 12)
- [ ] 100+ paying customers
- [ ] $20,000+ MRR
- [ ] Mobile app launched
- [ ] Operating profitability

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2025 | Initial SaaS charter |
