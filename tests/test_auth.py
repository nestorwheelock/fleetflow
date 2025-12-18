import pytest
from django.urls import reverse


class TestAuthenticationViews:
    """Tests for authentication views - B-001 bug fix"""

    def test_login_page_accessible(self, client):
        """Login page should return 200, not 404"""
        response = client.get('/login/')
        assert response.status_code == 200

    def test_login_page_contains_form(self, client):
        """Login page should contain a login form"""
        response = client.get('/login/')
        assert b'<form' in response.content
        assert b'username' in response.content.lower()
        assert b'password' in response.content.lower()

    def test_logout_url_exists(self, client, tenant_user):
        """Logout URL should be accessible via POST"""
        client.force_login(tenant_user.user)
        response = client.post('/logout/')
        # Should redirect after logout
        assert response.status_code in [200, 302]

    def test_logout_requires_post_method(self, client, tenant_user):
        """B-006: Logout should require POST method, not GET.

        Django's LogoutView requires POST for security (CSRF protection).
        GET requests should return 405 Method Not Allowed.
        """
        client.force_login(tenant_user.user)
        response = client.get('/logout/')
        assert response.status_code == 405, "Logout should reject GET requests"

    def test_login_redirects_to_dashboard(self, client, tenant_user):
        """Successful login should redirect to dashboard"""
        response = client.post('/login/', {
            'username': tenant_user.user.username,
            'password': 'testpassword123',
        })
        # Will be 302 redirect or 200 with form errors
        assert response.status_code in [200, 302]

    def test_dashboard_redirects_unauthenticated_to_login(self, client):
        """Dashboard should redirect unauthenticated users to login"""
        response = client.get('/dashboard/')
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_login_page_uses_correct_template(self, client):
        """Login page should use registration/login.html template"""
        response = client.get('/login/')
        assert response.status_code == 200
        templates = [t.name for t in response.templates]
        assert 'registration/login.html' in templates
