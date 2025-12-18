# B-006: Logout Returns 405 Method Not Allowed

**Severity**: High
**Affected Component**: Authentication
**Discovered**: 2025-12-18

## Bug Description

When clicking the logout button, users receive a "405 Method Not Allowed" error instead of being logged out.

## Steps to Reproduce

1. Log in to the application
2. Click the logout button/link
3. Observe error: "http://localhost:9091/logout/ sent back an error. Error code: 405 Method Not Allowed"

## Expected Behavior

User should be logged out and redirected to the login page.

## Actual Behavior

405 Method Not Allowed error is returned.

## Root Cause Analysis

The logout URL is likely configured to only accept POST requests (for CSRF protection), but the logout link/button is making a GET request. Or the view is not properly configured to accept the request method being used.

## Proposed Fix

1. Check if logout link is using correct HTTP method (POST with CSRF token)
2. Or configure LogoutView to accept GET requests
3. Update logout button to be a form with POST method if needed

## Files to Investigate

- `templates/base.html` or navigation template - check logout link
- `config/urls.py` - check logout URL configuration
- `apps/dashboard/urls.py` - if logout is handled there

## Acceptance Criteria

- [ ] Users can successfully log out
- [ ] Redirect to login page after logout
- [ ] CSRF protection maintained (use POST with token)
- [ ] Test coverage for logout functionality
