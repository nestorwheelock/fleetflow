# FleetFlow Wireframes

## Overview

This directory contains ASCII wireframes for all major screens in the FleetFlow car rental management SaaS platform. These wireframes serve as visual specifications for the user interface implementation.

FleetFlow is a **multi-tenant SaaS platform** where each rental company (tenant) gets their own branded subdomain (e.g., `ronsrentals.fleetflow.com`). The wireframes cover:
- **Platform Admin** (Super Admin) - FleetFlow platform management
- **Tenant Dashboard** - Rental company staff management
- **Public Landing Pages** - Customer-facing branded pages
- **Customer Portal** - Self-service for rental customers

## Multi-Tenant Architecture

### URL Structure
```
fleetflow.com/                        → Marketing site / Platform login
fleetflow.com/admin-platform/         → Super Admin dashboard (purple theme)
ronsrentals.fleetflow.com/            → Tenant landing page (tenant branding)
ronsrentals.fleetflow.com/login/      → Tenant login (staff & customers)
ronsrentals.fleetflow.com/dashboard/  → Tenant staff dashboard
ronsrentals.fleetflow.com/customer/   → Customer self-service portal
rentals.ronscompany.com/              → Custom domain (same as subdomain)
```

### Theme Differentiation
| Interface | Theme | Primary Color |
|-----------|-------|---------------|
| Platform Admin | Purple/Dark | `#4c1d95` |
| Tenant Dashboard | Tenant Branding | `{{ tenant.branding.primary_color }}` |
| Public Pages | Tenant Branding | `{{ tenant.branding.primary_color }}` |
| Customer Portal | Tenant Branding | `{{ tenant.branding.primary_color }}` |

### Tenant Branding CSS Variables
```css
:root {
  --brand-primary: {{ tenant.branding.primary_color|default:'#2563eb' }};
  --brand-secondary: {{ tenant.branding.secondary_color|default:'#1e40af' }};
}
```

## Design Patterns

### Colors (Tailwind CSS)
- **Primary**: Blue (`blue-600`) - Main actions, navigation highlights (or tenant brand color)
- **Success**: Green (`green-500`) - Available, completed, positive states
- **Warning**: Yellow (`yellow-500`) - Pending, attention needed
- **Danger**: Red (`red-500`) - Overdue, errors, critical alerts
- **Neutral**: Gray (`gray-*`) - Backgrounds, borders, secondary text
- **Platform Admin**: Purple (`purple-900`) - Super admin interface

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

### Platform Super Admin Workflow
1. Login → Platform Dashboard
2. Dashboard → Tenant List → Tenant Detail → Impersonate User
3. Dashboard → Platform Settings → Toggle Features
4. Tenant Detail → Edit Plan/Limits → Save Changes
5. Tenant Detail → Suspend/Reactivate Tenant

### Tenant Staff Workflow
1. Login (subdomain) → Tenant Dashboard
2. Dashboard → Today's Schedule → Checkout/Checkin
3. Dashboard → Quick Actions → Create Reservation
4. Calendar → Click Date → Create Reservation
5. Vehicle List → Vehicle Detail → Create Reservation
6. Settings → Branding → Customize Colors/Logo
7. Settings → Domains → Add Custom Domain

### Customer Self-Service (Multi-Tenant)
1. Visit Landing Page → Browse Vehicles → Register
2. Register → Upload Documents (License + Insurance) → Await Verification
3. Documents Verified → Browse Vehicles → Book
4. Booking → Extras → Review → Payment → Confirmation
5. My Account → My Bookings → View Details
6. Upcoming Rental → Sign Contract → Ready for Pickup

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

### Super Admin Platform (W-028 to W-032)
| ID | Screen | Description |
|----|--------|-------------|
| W-028 | Platform Dashboard | Super admin overview with tenant metrics |
| W-029 | Tenant List | Searchable tenant list with filters |
| W-030 | Tenant Detail | Tenant stats, users, activity, edit settings |
| W-031 | User Impersonation | Impersonate flow with reason input, red banner |
| W-032 | Platform Settings | Feature toggles (email verification, custom domains) |

**File**: `W-028-to-W-032-super-admin.txt`
**Theme**: Purple/dark (`#4c1d95`) to distinguish from tenant interfaces
**Access**: `is_superuser=True` only

### Multi-Tenant Public Pages (W-033)
| ID | Screen | Description |
|----|--------|-------------|
| W-033 | Tenant Landing Page | Public branded landing page per tenant |

**File**: `W-033-tenant-landing-page.txt`
**Theme**: Tenant branding (colors, logo)
**URL**: `{subdomain}.fleetflow.com/`

### Tenant Settings & Customer Portal (W-034 to W-036)
| ID | Screen | Description |
|----|--------|-------------|
| W-034 | Customer Document Upload | License and insurance upload with verification workflow |
| W-035 | Tenant Branding Settings | Logo upload, color pickers, live preview |
| W-036 | Custom Domain Settings | Add domain, DNS instructions, verification status |

**File**: `W-034-to-W-036-tenant-settings.txt`
**Theme**: Tenant branding
**Access**: W-034 (customers), W-035-036 (tenant owners/admins)

## Document Verification States

Used in W-006 (Staff view) and W-034 (Customer view):

| State | Icon | Description |
|-------|------|-------------|
| Missing | 🔴 | Required document not uploaded |
| Pending | 🟡 | Document uploaded, awaiting staff review |
| Verified | ✓ | Document reviewed and approved |
| Rejected | ❌ | Document rejected, needs re-upload |

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
