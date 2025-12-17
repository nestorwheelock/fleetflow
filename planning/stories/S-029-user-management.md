# S-029: User Management & Roles

**Story Type**: User Story
**Priority**: High
**Estimate**: 2 days
**Sprint**: Epoch 1
**Status**: Pending

## User Story
**As a** rental business owner
**I want to** manage staff accounts with different permission levels
**So that** my team can use the system with appropriate access

## Acceptance Criteria
- [ ] Can invite staff members by email
- [ ] Can assign roles: Owner, Manager, Agent
- [ ] Owners have full access including billing
- [ ] Managers can manage vehicles, customers, reservations
- [ ] Agents can only process rentals (no settings access)
- [ ] Can deactivate staff accounts
- [ ] User count enforced per plan (1, 3, 10, unlimited)
- [ ] Invitation expires after 7 days

## Role Permissions Matrix

| Permission | Owner | Manager | Agent |
|------------|-------|---------|-------|
| Billing/Subscription | Yes | No | No |
| User Management | Yes | No | No |
| Settings | Yes | Yes | No |
| Vehicle Management | Yes | Yes | View |
| Customer Management | Yes | Yes | Yes |
| Reservations | Yes | Yes | Yes |
| Reports | Yes | Yes | Limited |

## Definition of Done
- [ ] User model extended with tenant FK and role
- [ ] Invitation system with email tokens
- [ ] Role-based permission decorators/mixins
- [ ] User limit enforcement per plan
- [ ] Staff management UI for owners
- [ ] Tests cover all permission scenarios (>95% coverage)
- [ ] Documentation for user management
