# S-034: Public API

**Story Type**: User Story
**Priority**: Low
**Estimate**: 4 days
**Sprint**: Epoch 5
**Status**: Pending

## User Story
**As a** car rental business owner (Business/Enterprise plan)
**I want to** access my FleetFlow data via API
**So that** I can integrate with my other business systems

## Acceptance Criteria
- [ ] REST API for vehicles, customers, reservations
- [ ] API key authentication
- [ ] Rate limiting per plan
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Webhooks for key events
- [ ] API usage tracking
- [ ] Only available on Business/Enterprise plans

## API Endpoints

### Vehicles
- `GET /api/v1/vehicles/` - List vehicles
- `GET /api/v1/vehicles/{id}/` - Get vehicle
- `POST /api/v1/vehicles/` - Create vehicle
- `PUT /api/v1/vehicles/{id}/` - Update vehicle
- `DELETE /api/v1/vehicles/{id}/` - Delete vehicle

### Customers
- `GET /api/v1/customers/` - List customers
- `GET /api/v1/customers/{id}/` - Get customer
- `POST /api/v1/customers/` - Create customer
- `PUT /api/v1/customers/{id}/` - Update customer

### Reservations
- `GET /api/v1/reservations/` - List reservations
- `GET /api/v1/reservations/{id}/` - Get reservation
- `POST /api/v1/reservations/` - Create reservation
- `PUT /api/v1/reservations/{id}/` - Update reservation
- `GET /api/v1/reservations/{id}/availability/` - Check availability

## Webhooks
- `reservation.created`
- `reservation.updated`
- `reservation.cancelled`
- `vehicle.status_changed`
- `payment.received`

## Definition of Done
- [ ] Django REST Framework API views
- [ ] API key authentication system
- [ ] Rate limiting middleware
- [ ] OpenAPI/Swagger documentation
- [ ] Webhook delivery system
- [ ] API usage logging
- [ ] Tests cover API endpoints (>95% coverage)
- [ ] API documentation site
