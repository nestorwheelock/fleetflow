# FleetFlow

<p align="center">
  <img src="assets/logos/fleetflow-logo-en.svg" alt="FleetFlow Logo" width="400">
</p>

### Car Rental Management Software for Growing Businesses

**Finally, rental software built for businesses like yours — not enterprise giants.**

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Status](https://img.shields.io/badge/status-Epoch%201%20Complete-green.svg)]()
[![Tests](https://img.shields.io/badge/tests-181%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)]()

---

## Quick Start (Development)

```bash
# Clone the repository
git clone https://github.com/nestorwheelock/fleetflow.git
cd fleetflow

# Start with Docker
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Create admin user
docker compose exec web python manage.py createsuperuser

# Access the app
open http://localhost:9199
open http://localhost:9199/admin
```

---

## Development Status

### Epoch 1: Core Operations (MVP) - COMPLETE

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

### Test Coverage

```
181 tests passing | 91% overall coverage
├── tenants:      96%
├── reservations: 97%
├── fleet:        73-96%
├── customers:    74-97%
├── contracts:    87-93%
└── dashboard:    85%
```

---

## Architecture

### Multi-Tenant SaaS Model

```
┌─────────────────────────────────────────────────────────────┐
│                    FleetFlow Platform                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Tenant A   │  │  Tenant B   │  │  Tenant C   │  ...    │
│  │  (Acme Car) │  │  (Best Rent)│  │  (Quick Car)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│  ┌──────┴────────────────┴────────────────┴──────┐         │
│  │            Shared PostgreSQL Database          │         │
│  │         (tenant_id isolation per row)          │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
fleetflow/
├── apps/                       # Django applications
│   ├── tenants/               # Multi-tenant core
│   │   ├── models.py          # Tenant, TenantUser
│   │   ├── middleware.py      # Tenant context injection
│   │   ├── mixins.py          # TenantViewMixin
│   │   └── views.py           # Tenant API
│   ├── fleet/                 # Vehicle management
│   │   ├── models.py          # Vehicle, VehicleCategory, VehiclePhoto
│   │   ├── serializers.py     # DRF serializers
│   │   └── views.py           # REST API + views
│   ├── customers/             # Customer management
│   │   ├── models.py          # Customer, CustomerDocument
│   │   └── views.py           # REST API + views
│   ├── reservations/          # Booking system
│   │   ├── models.py          # Reservation, ReservationExtra
│   │   └── views.py           # Calendar, availability, check-in/out
│   ├── contracts/             # Contract generation
│   │   ├── models.py          # Contract, ConditionReport
│   │   └── views.py           # PDF generation, signatures
│   └── dashboard/             # Staff interface
│       └── views.py           # Dashboard, quick actions
├── templates/                  # Tailwind CSS templates
├── tests/                      # 181 pytest tests
├── config/                     # Django settings
│   ├── settings/
│   │   ├── base.py            # Common settings
│   │   ├── development.py     # Dev settings
│   │   └── production.py      # Prod settings
│   └── urls.py                # URL routing
├── requirements/               # Dependencies
├── planning/                   # Planning documents
├── Dockerfile                  # Python 3.12 image
└── docker-compose.yml          # Full stack
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.x, Django REST Framework |
| **Database** | PostgreSQL 15 |
| **Cache/Queue** | Redis 7, Celery |
| **Frontend** | Tailwind CSS, HTMX, Alpine.js |
| **PDF Generation** | ReportLab |
| **Container** | Docker, Docker Compose |
| **Testing** | pytest, pytest-django, pytest-cov |

---

## API Endpoints

### Tenants
- `GET /api/tenants/` - List tenants
- `GET /api/tenants/{id}/stats/` - Tenant statistics
- `GET /api/tenants/{id}/users/` - Tenant users
- `GET /api/tenants/users/` - Tenant user management

### Fleet
- `GET /api/fleet/vehicles/` - List vehicles
- `POST /api/fleet/vehicles/` - Create vehicle
- `GET /api/fleet/vehicles/available/` - Available vehicles
- `POST /api/fleet/vehicles/{id}/set_status/` - Change status
- `GET /api/fleet/categories/` - Vehicle categories

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}/rentals/` - Rental history
- `POST /api/customers/{id}/blacklist/` - Blacklist customer
- `POST /api/customers/{id}/unblacklist/` - Remove from blacklist

### Reservations
- `GET /api/reservations/` - List reservations
- `POST /api/reservations/` - Create reservation
- `GET /api/reservations/calendar/` - Calendar view
- `GET /api/reservations/today/` - Today's schedule
- `GET /api/reservations/upcoming/` - Upcoming reservations
- `GET /api/reservations/check-availability/` - Check availability
- `POST /api/reservations/{id}/checkout/` - Check out vehicle
- `POST /api/reservations/{id}/checkin/` - Check in vehicle
- `POST /api/reservations/{id}/cancel/` - Cancel reservation

### Contracts
- `GET /api/contracts/` - List contracts
- `GET /api/contracts/{id}/pdf/` - View PDF
- `GET /api/contracts/{id}/download/` - Download PDF
- `POST /api/contracts/{id}/sign/` - Sign contract
- `POST /api/contracts/{id}/condition-report/` - Add condition report

### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics
- `GET /api/dashboard/today/` - Today's checkouts/checkins
- `GET /api/dashboard/revenue/` - Revenue summary
- `GET /api/dashboard/fleet-status/` - Fleet status counts
- `GET /api/dashboard/upcoming/` - Upcoming reservations
- `POST /api/dashboard/quick-actions/new-reservation/` - Quick reservation
- `POST /api/dashboard/quick-actions/new-customer/` - Quick customer
- `POST /api/dashboard/quick-actions/vehicle-status/` - Quick status change

---

## Subscription Plans

| Plan | Vehicles | Users | Price | Key Features |
|------|----------|-------|-------|--------------|
| **Starter** | 10 | 1 | $99/mo | Core features |
| **Professional** | 25 | 3 | $199/mo | + Online booking |
| **Business** | 50 | 10 | $349/mo | + GPS, analytics |
| **Enterprise** | Unlimited | Unlimited | Custom | Full platform |

---

## Running Tests

```bash
# Run all tests
docker compose exec web pytest tests/ -v

# Run with coverage
docker compose exec web pytest tests/ --cov=apps --cov-report=html

# Run specific test file
docker compose exec web pytest tests/test_reservations.py -v
```

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plans.

| Epoch | Status | Description |
|-------|--------|-------------|
| **1** | Done | Core Operations (MVP) |
| **2** | Planned | Online Booking & Payments |
| **3** | Planned | Advanced Features & Integrations |
| **4** | Planned | Mobile App |
| **5** | Planned | Platform & Growth |

---

## Documentation

- [Project Charter](planning/PROJECT_CHARTER.md)
- [SPEC Summary](planning/SPEC_SUMMARY.md)
- [User Stories](planning/stories/)
- [Tasks](planning/tasks/)
- [Wireframes](planning/wireframes/)
- [Roadmap](ROADMAP.md)

---

## Contact

- **GitHub**: https://github.com/nestorwheelock/fleetflow
- **Developer**: https://linuxremotesupport.com

---

## License

**Proprietary License** — All Rights Reserved

---

*FleetFlow — Car rental software that actually fits your business.*
