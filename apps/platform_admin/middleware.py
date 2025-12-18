"""
Platform Admin Middleware

Handles user impersonation sessions.
"""
from django.utils import timezone
from .models import ImpersonationLog

IMPERSONATION_SESSION_KEY = '_impersonate_user_id'
IMPERSONATION_LOG_KEY = '_impersonate_log_id'


class ImpersonationMiddleware:
    """
    Middleware that handles user impersonation.

    When a superuser is impersonating another user:
    - request.user is set to the impersonated user
    - request.impersonator is set to the actual superuser
    - request.is_impersonating is set to True

    The impersonation is stored in the session and persists across requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Default values
        request.impersonator = None
        request.is_impersonating = False
        request.impersonation_log = None

        # Check if user is impersonating someone
        if request.user.is_authenticated:
            impersonate_user_id = request.session.get(IMPERSONATION_SESSION_KEY)
            impersonate_log_id = request.session.get(IMPERSONATION_LOG_KEY)

            if impersonate_user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()

                try:
                    # Get the impersonated user
                    impersonated_user = User.objects.get(pk=impersonate_user_id)

                    # Store the real user (superuser) as impersonator
                    request.impersonator = request.user

                    # Replace request.user with impersonated user
                    request.user = impersonated_user
                    request.is_impersonating = True

                    # Get the impersonation log
                    if impersonate_log_id:
                        try:
                            request.impersonation_log = ImpersonationLog.objects.get(pk=impersonate_log_id)
                        except ImpersonationLog.DoesNotExist:
                            pass

                except User.DoesNotExist:
                    # User no longer exists, clear impersonation
                    self.end_impersonation(request)

        response = self.get_response(request)
        return response

    @staticmethod
    def start_impersonation(request, target_user, reason):
        """
        Start impersonating a user.

        Args:
            request: The HTTP request
            target_user: The user to impersonate
            reason: Reason for impersonation (ticket number, etc.)

        Returns:
            ImpersonationLog: The created log entry
        """
        from .models import get_client_ip

        # Get tenant context if available
        tenant = getattr(request, 'tenant', None)

        # Create impersonation log
        log = ImpersonationLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            tenant=tenant,
            reason=reason,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )

        # Store in session
        request.session[IMPERSONATION_SESSION_KEY] = target_user.pk
        request.session[IMPERSONATION_LOG_KEY] = log.pk

        return log

    @staticmethod
    def end_impersonation(request):
        """
        End the current impersonation session.

        Args:
            request: The HTTP request

        Returns:
            bool: True if impersonation was ended, False if not impersonating
        """
        log_id = request.session.get(IMPERSONATION_LOG_KEY)

        # Update the impersonation log
        if log_id:
            try:
                log = ImpersonationLog.objects.get(pk=log_id)
                log.ended_at = timezone.now()
                log.save()
            except ImpersonationLog.DoesNotExist:
                pass

        # Clear session data
        if IMPERSONATION_SESSION_KEY in request.session:
            del request.session[IMPERSONATION_SESSION_KEY]
        if IMPERSONATION_LOG_KEY in request.session:
            del request.session[IMPERSONATION_LOG_KEY]

        return True
