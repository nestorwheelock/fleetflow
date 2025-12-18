"""
Platform Administration Models

Models for managing the FleetFlow SaaS platform at a super-admin level.
These models are platform-wide and not tenant-scoped.
"""
from django.db import models
from django.conf import settings
from django.core.cache import cache


class PlatformSettings(models.Model):
    """
    Singleton model for platform-wide settings.

    Controls features that affect all tenants, such as:
    - Email verification requirements
    - Custom domain support
    - Customer self-registration
    """

    # Feature toggles
    require_email_verification = models.BooleanField(
        default=False,
        help_text='Require email verification for new user accounts'
    )
    allow_custom_domains = models.BooleanField(
        default=True,
        help_text='Allow tenants to configure custom domains'
    )
    allow_customer_registration = models.BooleanField(
        default=True,
        help_text='Allow customers to self-register on tenant sites'
    )

    # Platform branding
    platform_name = models.CharField(
        max_length=100,
        default='FleetFlow',
        help_text='Name displayed in platform-level interfaces'
    )

    # Maintenance mode
    maintenance_mode = models.BooleanField(
        default=False,
        help_text='Enable maintenance mode (blocks all non-superuser access)'
    )
    maintenance_message = models.TextField(
        blank=True,
        default='We are currently performing scheduled maintenance. Please check back soon.',
        help_text='Message shown during maintenance mode'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Platform Settings'
        verbose_name_plural = 'Platform Settings'

    def __str__(self):
        return f'Platform Settings (updated {self.updated_at})'

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear cache when settings change
        cache.delete('platform_settings')

    @classmethod
    def get_settings(cls):
        """
        Get the singleton settings instance.

        Uses caching for performance. Creates default settings if none exist.
        """
        settings_obj = cache.get('platform_settings')
        if settings_obj is None:
            settings_obj, _ = cls.objects.get_or_create(pk=1)
            cache.set('platform_settings', settings_obj, timeout=300)  # 5 minutes
        return settings_obj

    @classmethod
    def get_solo(cls):
        """Alias for get_settings() for compatibility."""
        return cls.get_settings()


class ImpersonationLog(models.Model):
    """
    Audit log for user impersonation sessions.

    Records every impersonation event for security and compliance.
    """
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impersonation_sessions',
        help_text='The super admin who initiated the impersonation'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impersonated_sessions',
        help_text='The user being impersonated'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The tenant context during impersonation'
    )

    # Session details
    reason = models.TextField(
        help_text='Reason for impersonation (ticket number, support request, etc.)'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Impersonation Log'
        verbose_name_plural = 'Impersonation Logs'

    def __str__(self):
        return f'{self.admin_user.email} → {self.target_user.email} ({self.started_at})'

    @property
    def is_active(self):
        """Check if this impersonation session is still active."""
        return self.ended_at is None

    @property
    def duration(self):
        """Get the duration of the impersonation session."""
        if self.ended_at:
            return self.ended_at - self.started_at
        from django.utils import timezone
        return timezone.now() - self.started_at


class PlatformAuditLog(models.Model):
    """
    Audit log for platform-level administrative actions.

    Records all significant actions taken by super admins.
    """
    ACTION_CHOICES = [
        ('tenant_create', 'Tenant Created'),
        ('tenant_update', 'Tenant Updated'),
        ('tenant_suspend', 'Tenant Suspended'),
        ('tenant_reactivate', 'Tenant Reactivated'),
        ('tenant_delete', 'Tenant Deleted'),
        ('user_create', 'User Created'),
        ('user_update', 'User Updated'),
        ('user_delete', 'User Deleted'),
        ('impersonate_start', 'Impersonation Started'),
        ('impersonate_end', 'Impersonation Ended'),
        ('settings_update', 'Platform Settings Updated'),
        ('plan_change', 'Subscription Plan Changed'),
        ('feature_toggle', 'Feature Flag Toggled'),
    ]

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='platform_audit_logs',
        help_text='The admin who performed the action'
    )
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        help_text='Type of action performed'
    )

    # Target (optional, depends on action type)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Tenant affected by this action (if applicable)'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='platform_actions_received',
        help_text='User affected by this action (if applicable)'
    )

    # Change details
    description = models.TextField(
        blank=True,
        help_text='Human-readable description of the action'
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text='JSON object with before/after values for changes'
    )

    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Platform Audit Log'
        verbose_name_plural = 'Platform Audit Logs'

    def __str__(self):
        return f'{self.get_action_display()} by {self.admin_user} at {self.timestamp}'


def log_platform_action(
    admin_user,
    action,
    tenant=None,
    target_user=None,
    description='',
    changes=None,
    request=None
):
    """
    Helper function to create a platform audit log entry.

    Args:
        admin_user: The admin performing the action
        action: Action type (from ACTION_CHOICES)
        tenant: Optional tenant affected
        target_user: Optional user affected
        description: Human-readable description
        changes: Dict with before/after values
        request: HTTP request for IP/user agent extraction
    """
    ip_address = None
    user_agent = ''

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    return PlatformAuditLog.objects.create(
        admin_user=admin_user,
        action=action,
        tenant=tenant,
        target_user=target_user,
        description=description,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
