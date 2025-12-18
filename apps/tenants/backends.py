"""
Custom authentication backends for FleetFlow multi-tenant SaaS.

Supports:
- Email-based authentication (case-insensitive)
- Integration with tenant context
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email address (case-insensitive).

    This backend replaces username-based authentication with email-based
    authentication for the entire platform.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate a user by email and password.

        Args:
            request: The HTTP request object
            email: The user's email address (case-insensitive)
            password: The user's password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Support both 'email' and 'username' parameters for compatibility
        if email is None:
            email = kwargs.get('username')

        if email is None or password is None:
            return None

        try:
            # Case-insensitive email lookup
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing
            # side-channel attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        """Retrieve a user by their primary key."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
