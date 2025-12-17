# FleetFlow Wireframes

## Overview

This directory contains ASCII wireframes for all major screens in the FleetFlow car rental management system. These wireframes serve as visual specifications for the user interface implementation.

## Design Patterns

### Colors (Tailwind CSS)
- **Primary**: Blue (`blue-600`) - Main actions, navigation highlights
- **Success**: Green (`green-500`) - Available, completed, positive states
- **Warning**: Yellow (`yellow-500`) - Pending, attention needed
- **Danger**: Red (`red-500`) - Overdue, errors, critical alerts
- **Neutral**: Gray (`gray-*`) - Backgrounds, borders, secondary text

### Typography
- **Headings**: Inter font family, semi-bold/bold weights
- **Body**: Inter font family, regular weight
- **Monospace**: For confirmation numbers, VINs, license plates

### Spacing
- Container max-width: 1280px (7xl)
- Padding: 4-6 units (1rem-1.5rem)
- Card spacing: 6 units between cards

### Components
- **Cards**: Rounded corners (`rounded-lg`), shadow (`shadow`)
- **Buttons**: Rounded (`rounded-md`), consistent padding
- **Tables**: Striped rows, hover states
- **Forms**: Stacked labels, full-width inputs

## User Flows

### Staff Workflow
1. Login → Dashboard
2. Dashboard → Today's Schedule → Checkout/Checkin
3. Dashboard → Quick Actions → Create Reservation
4. Calendar → Click Date → Create Reservation
5. Vehicle List → Vehicle Detail → Create Reservation

### Customer Self-Service (Epoch 2+)
1. Browse Vehicles → Select Vehicle → Booking Flow
2. Booking → Extras → Review → Payment → Confirmation
3. My Account → My Rentals → View Details
4. Upcoming Rental → Sign Contract → Ready for Pickup

### Mobile App (Epoch 4)
1. Login → Home Dashboard
2. Home → Find My Car → Map View
3. Home → Browse → Vehicle Detail → Book
4. My Rentals → Documents → QR Code Check-in

## Wireframe Index

### Epoch 1: Core Rental Operations (W-001 to W-008)
| ID | Screen | Description |
|----|--------|-------------|
| W-001 | Staff Dashboard | Main dashboard with schedule and stats |
| W-002 | Vehicle List | Vehicle fleet management list view |
| W-003 | Vehicle Detail | Individual vehicle information |
| W-004 | Reservation Calendar | Calendar view with bookings |
| W-005 | New Reservation Form | Multi-step reservation creation |
| W-006 | Customer List & Detail | Customer management views |
| W-007 | Check-Out Process | Vehicle pickup workflow |
| W-008 | Contract View | Rental agreement display |

### Epoch 2: Self-Service Portal (W-009 to W-014)
| ID | Screen | Description |
|----|--------|-------------|
| W-009 | Customer Registration | Account creation form |
| W-010 | Customer Portal Dashboard | Self-service home page |
| W-011 | Public Vehicle Catalog | Browse vehicles (public) |
| W-012 | Online Booking Flow | Step-by-step booking |
| W-013 | PayPal Checkout | Payment integration |
| W-014 | E-Signature Contract | Digital contract signing |

### Epoch 3: Advanced Features (W-015 to W-019)
| ID | Screen | Description |
|----|--------|-------------|
| W-015 | Maintenance Calendar | Service scheduling |
| W-016 | GPS Fleet Tracking | Real-time map view |
| W-017 | License Verification | Document validation |
| W-018 | Analytics Dashboard | Reports and metrics |
| W-019 | Mobile Booking | Responsive booking flow |

### Epoch 4: Mobile App (W-020 to W-027)
| ID | Screen | Description |
|----|--------|-------------|
| W-020 | Mobile Login | App authentication |
| W-021 | Mobile Home | App dashboard |
| W-022 | Vehicle Location Map | Find car feature |
| W-023 | Trip Sharing | Share location with family |
| W-024 | Shared Trip Viewer | Web view for non-app users |
| W-025 | Mobile Booking Flow | Native booking screens |
| W-026 | Mobile Documents | QR code check-in |
| W-027 | Push Notifications | Notification examples |

## Responsive Breakpoints

- **Desktop**: > 1024px (default wireframes)
- **Tablet**: 768px - 1024px (sidebar collapses)
- **Mobile**: < 768px (stacked layout)

## Accessibility Notes

- All forms have associated labels
- Color is not the only indicator of state (icons/text included)
- Keyboard navigation supported
- Focus states visible
- Screen reader friendly semantic HTML
