# FleetFlow - Project Charter

## Project Overview

**Project Name**: FleetFlow - Car Rental Management System
**Version**: v1.0.0 (Epoch 1 MVP)
**Start Date**: December 2024
**Project Type**: Web Application + Mobile App

---

## Executive Summary

FleetFlow is a comprehensive car rental management system designed for small local rental businesses (10-50 vehicles, single location). The system provides end-to-end rental operations including fleet management, customer management, reservations, payments, contracts, maintenance tracking, and a customer self-service portal with mobile app support.

---

## Business Objectives

### Primary Goals
1. **Streamline Operations** - Replace manual/paper-based processes with digital workflows
2. **Enable Self-Service** - Allow customers to browse, book, and pay online
3. **Improve Fleet Utilization** - Track vehicle availability and maintenance efficiently
4. **Reduce Errors** - Prevent double-bookings and missed maintenance
5. **Enhance Customer Experience** - Mobile app with real-time vehicle tracking

### Success Metrics
- 80% reduction in manual paperwork
- 50% of bookings completed online (self-service)
- 95% fleet utilization visibility
- Zero double-bookings
- Customer satisfaction score > 4.5/5

---

## Scope

### In Scope (4 Epochs)

**Epoch 1: Core Rental Operations (MVP)**
- Vehicle fleet management (CRUD, photos, rates)
- Customer management (profiles, documents, history)
- Reservation calendar with conflict prevention
- Check-out/check-in workflows with condition reports
- PDF contract generation
- Staff dashboard

**Epoch 2: Self-Service Portal & Payments**
- Customer registration and authentication
- Online vehicle browsing and booking
- PayPal payment integration
- Electronic contract signing (e-signatures)
- Email notifications and reminders

**Epoch 3: Advanced Features & Integrations**
- Maintenance scheduling and tracking
- GPS/telematics fleet tracking
- Driver license verification API
- Insurance verification
- Business analytics and reports
- PWA support

**Epoch 4: Mobile App with Driver Tracking**
- React Native mobile app (iOS/Android)
- Biometric authentication
- Real-time vehicle GPS tracking
- Trip sharing for safety
- Push notifications
- Offline mode with sync
- Digital documents and QR check-in

### Out of Scope (Future Versions)
- Multi-location support
- Franchise management
- Vehicle auction/sales module
- Full accounting/ERP integration
- International currency support
- Digital key/keyless entry
- AI-powered pricing optimization

---

## Technical Architecture

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.x, Python 3.12+ |
| Database | PostgreSQL 15 |
| Task Queue | Celery + Redis |
| API | Django REST Framework |
| Real-time | Django Channels (WebSocket) |
| Frontend (Web) | Django Templates, Tailwind CSS, HTMX, Alpine.js |
| Frontend (Mobile) | React Native, Expo |
| Payments | PayPal SDK |
| Maps | MapBox / Google Maps |
| Push Notifications | Firebase Cloud Messaging |
| File Storage | AWS S3 (production) / Local (dev) |
| PDF Generation | ReportLab |

### System Components

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼─────┐        ┌────▼────┐
   │  Web    │         │   API     │        │ Mobile  │
   │ Portal  │         │  Server   │        │   App   │
   └────┬────┘         └─────┬─────┘        └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Django Core    │
                    │  Application    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼─────┐        ┌────▼────┐
   │PostgreSQL│         │   Redis   │        │   S3    │
   │ Database │         │   Cache   │        │ Storage │
   └──────────┘         └───────────┘        └─────────┘
```

---

## Stakeholders

| Role | Responsibility |
|------|----------------|
| Business Owner | Requirements, approval, funding |
| Developer | Design, implementation, testing |
| End Users (Staff) | Daily rental operations |
| End Users (Customers) | Self-service booking and management |

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PayPal API changes | High | Low | Abstract payment layer, monitor API updates |
| GPS hardware compatibility | Medium | Medium | Support multiple providers, graceful fallback |
| Mobile app store rejection | Medium | Low | Follow guidelines, beta testing |
| Data loss | High | Low | Automated backups, redundant storage |
| Security breach | High | Low | OWASP compliance, security audits, encryption |

---

## Assumptions

1. Business operates single location (multi-location out of scope)
2. Fleet size 10-50 vehicles (scalable architecture for growth)
3. Staff has basic computer literacy
4. Customers have smartphones for mobile app
5. Reliable internet connectivity at rental location
6. GPS hardware will be installed in vehicles (Epoch 3)

---

## Constraints

1. **Budget**: AI-assisted development model with fixed pricing per epoch
2. **Timeline**: Sequential epoch delivery
3. **Technology**: Django/Python backend (per client preference)
4. **Payments**: PayPal only (per client preference)
5. **Mobile**: Cross-platform (React Native) vs native

---

## Acceptance Criteria

### Epoch 1 (MVP) Acceptance
- [ ] Staff can add/edit/view vehicles with photos and rates
- [ ] Staff can add/edit/view customers with license info
- [ ] Staff can create reservations on calendar
- [ ] System prevents double-booking same vehicle
- [ ] Staff can process check-out with condition report
- [ ] Staff can process check-in with final charges
- [ ] System generates PDF rental contracts
- [ ] Dashboard shows daily pickups/returns
- [ ] All features have >95% test coverage

### Epoch 2 Acceptance
- [ ] Customers can register and login
- [ ] Customers can browse available vehicles
- [ ] Customers can complete online booking
- [ ] PayPal payment processing works
- [ ] Customers can e-sign contracts
- [ ] Email notifications sent for bookings

### Epoch 3 Acceptance
- [ ] Maintenance scheduling and alerts work
- [ ] GPS tracking displays on map
- [ ] License verification API integrated
- [ ] Analytics dashboard shows key metrics
- [ ] Reports exportable to CSV/PDF

### Epoch 4 Acceptance
- [ ] Mobile app published to app stores
- [ ] Biometric login works
- [ ] Real-time vehicle location updates
- [ ] Trip sharing generates working links
- [ ] Push notifications delivered
- [ ] Offline mode caches rental data

---

## Approval

This Project Charter defines the scope, objectives, and approach for the FleetFlow Car Rental Management System. By approving this document, stakeholders agree to the defined scope and commit to the project.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Owner | | | |
| Developer | | | |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | Developer | Initial charter |
