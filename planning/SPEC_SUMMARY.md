# FleetFlow - SPEC Summary

## Quick Reference

| Item | Value |
|------|-------|
| **Project Name** | FleetFlow - Car Rental Management System |
| **Technology** | Django 5.x + PostgreSQL + Tailwind CSS + HTMX |
| **Business Type** | Small local rental (single location, 10-50 vehicles) |
| **Payment Provider** | PayPal |
| **Epochs** | 4 (Core, Portal, Advanced, Mobile) |
| **User Stories** | 26 total (S-001 to S-026) |
| **Tasks (Epoch 1)** | 24 tasks (T-001 to T-024) |
| **Wireframes** | 27 screens (W-001 to W-027) |

---

## Epoch Overview

### Epoch 1: Core Rental Operations (MVP)
**Goal**: Functional rental system for staff to manage vehicles, customers, and reservations

| Story | Description | Tasks |
|-------|-------------|-------|
| S-001 | Vehicle Fleet Management | T-001 to T-005 |
| S-002 | Customer Management | T-006 to T-009 |
| S-003 | Reservation Calendar System | T-010 to T-014 |
| S-004 | Rental Workflow (Check-out/Check-in) | T-015 to T-018 |
| S-005 | Basic Contract Generation | T-019 to T-021 |
| S-006 | Staff Dashboard | T-022 to T-024 |

### Epoch 2: Self-Service Portal & Payments
**Goal**: Customer-facing portal with online booking and PayPal payments

| Story | Description |
|-------|-------------|
| S-007 | Customer Self-Service Portal |
| S-008 | Online Vehicle Browsing |
| S-009 | Online Reservation Booking |
| S-010 | PayPal Payment Integration |
| S-011 | Electronic Contract Signing |
| S-012 | Customer Notifications |

### Epoch 3: Advanced Features & Integrations
**Goal**: Maintenance scheduling, GPS tracking, license verification, reporting

| Story | Description |
|-------|-------------|
| S-013 | Maintenance Scheduling System |
| S-014 | GPS Telematics Integration |
| S-015 | Driver License Verification |
| S-016 | Insurance Integration |
| S-017 | Reports and Analytics Dashboard |
| S-018 | Mobile-Optimized Experience |

### Epoch 4: Mobile App with Driver Tracking
**Goal**: Native mobile app for customers with real-time GPS tracking

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

---

## Key Models (Epoch 1)

### Vehicle
- make, model, year, vin, license_plate
- color, mileage, fuel_type, transmission, seats
- category, features (JSON), daily_rate, weekly_rate, monthly_rate
- status: available, rented, maintenance, retired
- deposit_amount, mileage_limit_per_day, extra_mileage_rate

### Customer
- first_name, last_name, email, phone
- address, city, state, zip_code
- license_number, license_state, license_expiry, date_of_birth
- verified, flag (vip/banned/none)

### Reservation
- confirmation_number (auto-generated)
- vehicle (FK), customer (FK)
- pickup_date, pickup_time, return_date, return_time
- daily_rate, subtotal, tax_amount, total_amount, deposit_amount
- status: pending, confirmed, in_progress, completed, cancelled
- pickup_mileage, return_mileage

### Contract
- contract_number, reservation (FK)
- terms_version, rental_terms, special_conditions
- signature_data, signed_at, signer_ip_address
- status: draft, pending_signature, signed, voided
- document_pdf (FileField)

---

## Technology Stack

### Backend
- Django 5.x
- PostgreSQL 15
- Django REST Framework
- Celery + Redis (background tasks)
- Django Channels (WebSocket for real-time)

### Frontend (Web)
- Django Templates
- Tailwind CSS
- HTMX
- Alpine.js
- FullCalendar.js

### Mobile (Epoch 4)
- React Native + Expo
- MapBox/Google Maps SDK
- Firebase Cloud Messaging

### Integrations
- PayPal SDK
- ReportLab (PDF)
- Pillow (images)
- AWS S3 (file storage)

---

## Pricing Configuration

| Setting | Value |
|---------|-------|
| Tax Rate | 8% |
| Mileage Limit | 150 mi/day |
| Extra Mileage | $0.25/mile |
| Fuel Price | $4.50/gallon |
| Late Fee (hourly) | $15/hour |
| Late Fee Max Hours | 3 (then full day) |
| Cleaning Fee | $75 |
| Basic Insurance | $10/day |
| Premium Insurance | $18/day |
| GPS | $5/day |
| Child Seat | $8/day |
| Additional Driver | $10/day |

---

## Document Links

### Planning Documents
- [Project Charter](PROJECT_CHARTER.md)
- [User Stories](stories/)
- [Task Documents](tasks/)
- [Wireframes](wireframes/)

### User Stories by Epoch
- [S-001 Vehicle Fleet Management](stories/S-001-vehicle-fleet-management.md)
- [S-002 Customer Management](stories/S-002-customer-management.md)
- [S-003 Reservation Calendar](stories/S-003-reservation-calendar.md)
- [S-004 Rental Workflow](stories/S-004-rental-workflow.md)
- [S-005 Contract Generation](stories/S-005-contract-generation.md)
- [S-006 Staff Dashboard](stories/S-006-staff-dashboard.md)

### Key Wireframes
- [W-001 Staff Dashboard](wireframes/W-001-staff-dashboard.txt)
- [W-004 Reservation Calendar](wireframes/W-004-reservation-calendar.txt)
- [W-007 Check-Out Process](wireframes/W-007-checkout-process.txt)

---

## Acceptance Criteria Summary

### Epoch 1 Must-Have Features
1. Add/edit/view vehicles with photos and rates
2. Add/edit/view customers with license info
3. Create/view reservations on calendar
4. Prevent double-booking (conflict detection)
5. Check-out workflow with condition report
6. Check-in workflow with final charges
7. Generate PDF contracts
8. Staff dashboard with daily schedule

### Quality Standards
- Test coverage > 95%
- API response time < 200ms (95th percentile)
- Frontend load < 2 seconds
- Mobile-responsive design
- Accessible (WCAG 2.1 AA)

---

## Estimated Effort

| Epoch | Human-Equivalent Hours | AI-Assisted Cost (60% discount) |
|-------|------------------------|--------------------------------|
| Epoch 1 | 40-50 hours | $1,600-2,000 |
| Epoch 2 | 35-45 hours | $1,400-1,800 |
| Epoch 3 | 40-50 hours | $1,600-2,000 |
| Epoch 4 | 45-55 hours | $1,800-2,200 |
| **Total** | **160-200 hours** | **$6,400-8,000** |

---

## Approval Status

- [ ] SPEC Phase Complete
- [ ] Client Approval Gate #1 (Issue #1)
- [ ] BUILD Phase Complete
- [ ] VALIDATION Phase Complete
- [ ] ACCEPTANCE TEST Phase Complete
- [ ] Client Approval Gate #2
- [ ] SHIP Phase Complete
