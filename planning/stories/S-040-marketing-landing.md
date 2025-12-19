# S-040: FleetFlow Marketing Landing Page

**Story Type**: User Story
**Priority**: High
**Estimate**: 1 day
**Sprint**: Sprint 8
**Status**: Completed

## User Story
**As a** visitor to fleetflow.com
**I want to** understand what FleetFlow offers and how to get started
**So that** I can decide if it's right for my rental business or find a rental car

## Acceptance Criteria

### Hero & Navigation
- [x] Hero section clearly explains FleetFlow's value proposition
- [x] Navigation includes Features, Pricing, and Login links
- [x] Header is consistent across all marketing pages

### Dual-Audience CTA
- [x] Left column: Car owners can enter email to start free trial
- [x] Right column: Renters can search by location
- [x] Both paths clearly differentiated with icons and messaging

### How It Works Section
- [x] Shows 3-step process: Sign Up -> Add Cars -> Get Paid
- [x] Uses visual icons for each step
- [x] Clear and simple messaging

### Pricing Section
- [x] Shows Personal (Free), Starter, Professional tiers on homepage
- [x] Links to full pricing page with all 5 tiers
- [x] Pricing includes per-rental fees and vehicle limits

### Social Proof
- [x] Testimonial section with customer quotes
- [x] Star ratings displayed
- [x] Customer name and business shown

### Features Grid
- [x] Highlights 6 key capabilities
- [x] Smart Scheduling, Digital Contracts, Real-Time Analytics
- [x] Customer Portal, Branded Website, Mobile Ready

### Referral System
- [x] Referral section lets visitors send $25 credits to friends
- [x] Captures referrer email, referred email, and referral type
- [x] Stores referrals in database (ReferralCredit model)
- [x] Prevents self-referral

### Lead Capture
- [x] Email signup form captures leads for follow-up
- [x] Leads stored in database (LeadCapture model)
- [x] Handles duplicate emails gracefully

### Rental Search
- [x] Search form accepts location query
- [x] Shows matching tenant businesses
- [x] Links to tenant subdomains
- [x] Shows empty state when no results

### Footer & Navigation
- [x] Footer has navigation links organized by category
- [x] Links to Privacy Policy, Terms of Service
- [x] Social media placeholder links
- [x] Copyright notice

### Technical Requirements
- [x] Fully responsive (mobile/tablet/desktop)
- [x] No authentication required to view
- [x] All forms use AJAX for smooth UX
- [x] Error handling for invalid inputs

## Definition of Done
- [x] All acceptance criteria implemented
- [x] Tests written and passing (30 tests, >95% coverage on marketing app)
- [x] Responsive design verified on mobile and desktop
- [x] Documentation updated (wireframe W-034 created)
- [x] Code committed and pushed to GitHub

## Technical Implementation

### Models Created
- `LeadCapture` - Stores email signups with lead type and source
- `ReferralCredit` - Tracks referral relationships and credit amounts

### Views Created
- `HomePageView` - Marketing homepage with all sections
- `PricingView` - Detailed pricing page with FAQ
- `FeaturesView` - Features overview page
- `RentalSearchView` - Tenant search by location
- `LeadCaptureView` - AJAX endpoint for lead capture
- `ReferralView` - AJAX endpoint for referral submissions

### Templates Created
- `templates/marketing/base.html` - Marketing base with header/footer
- `templates/marketing/home.html` - Full homepage
- `templates/marketing/pricing.html` - Pricing page
- `templates/marketing/features.html` - Features page
- `templates/marketing/search_results.html` - Search results

### URL Structure
- `/` - Marketing homepage
- `/pricing/` - Pricing page
- `/features/` - Features page
- `/search/` - Rental search
- `/api/lead/` - Lead capture endpoint
- `/api/referral/` - Referral endpoint

## Related Documents
- Wireframe: [W-034-marketing-landing.txt](../wireframes/W-034-marketing-landing.txt)
- Plan file: `/home/nwheelo/.claude/plans/partitioned-gathering-nebula.md`
