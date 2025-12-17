# S-001: Vehicle Fleet Management

**Story Type**: User Story
**Priority**: High
**Estimate**: 5 days
**Sprint**: Epoch 1
**Status**: PENDING

## User Story
**As a** rental business owner
**I want to** manage my vehicle fleet in one place
**So that** I can track all vehicles, their status, and availability

## Acceptance Criteria
- [ ] Can add new vehicles with full details (make, model, year, VIN, plate, mileage)
- [ ] Can upload multiple photos per vehicle (up to 10)
- [ ] Can set daily/weekly/monthly rental rates
- [ ] Can mark vehicles as available, rented, or out of service
- [ ] Can view all vehicles in list and grid views
- [ ] Can filter vehicles by status, category, availability
- [ ] Can edit and archive vehicles (soft delete)
- [ ] Can search vehicles by make, model, plate, or VIN

## Definition of Done
- [ ] Vehicle model created with all required fields
- [ ] Vehicle image model with multiple image support
- [ ] Admin interface configured for vehicle management
- [ ] List view with filtering and pagination
- [ ] Detail view with all vehicle information
- [ ] Grid view option for visual browsing
- [ ] Image upload with validation (size, type)
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-001: Django project setup and configuration
- T-002: Vehicle model and migrations
- T-003: Vehicle admin interface
- T-004: Vehicle list/detail views
- T-005: Vehicle image upload handling

## Notes
- Vehicle categories: Sedan, SUV, Truck, Van, Luxury, Economy
- Status options: Available, Rented, Maintenance, Reserved, Archived
- Fuel types: Gasoline, Diesel, Hybrid, Electric
- Transmission: Automatic, Manual
