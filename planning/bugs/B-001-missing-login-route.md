# B-001: Missing Login Route - 404 Error

**Severity**: Critical
**Affected Component**: Authentication / URL Routing
**Discovered**: December 2025

## Bug Description

Accessing the dashboard redirects to `/login/` which returns a 404 error. The login URL and view are not configured, but dashboard views use `@login_required` decorator which redirects unauthenticated users to the login page.

## Steps to Reproduce

1. Start the application: `docker compose up -d`
2. Navigate to `http://localhost:9199/dashboard/`
3. Observe redirect to `http://localhost:9199/login/?next=/dashboard/`
4. See 404 error - "Page not found"

## Expected Behavior

- User should see a login form
- After login, user should be redirected to the dashboard

## Actual Behavior

- 404 error: "The current path, login/, didn't match any of these."

## Root Cause

Django's `@login_required` decorator defaults to redirecting to `/accounts/login/` or the `LOGIN_URL` setting. The project has no authentication URLs configured in `config/urls.py`.

## Fix Required

1. Add Django's built-in auth URLs to `config/urls.py`
2. Create login/logout templates
3. Set `LOGIN_URL` and `LOGIN_REDIRECT_URL` in settings
4. Create basic login template with Tailwind styling

## Environment

- Django: 5.x
- Python: 3.12
- Docker: docker compose

## Related Files

- `config/urls.py` - Missing auth URLs
- `config/settings/base.py` - Missing LOGIN_URL setting
- `templates/registration/login.html` - Does not exist
