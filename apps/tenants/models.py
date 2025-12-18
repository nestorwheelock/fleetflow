from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType


class Tenant(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]

    SUBSCRIPTION_STATUS_CHOICES = [
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_tenants'
    )

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default='trialing'
    )

    vehicle_limit = models.IntegerField(default=10)
    user_limit = models.IntegerField(default=1)
    features = models.JSONField(default=dict, blank=True)

    business_name = models.CharField(max_length=200)
    business_address = models.TextField(blank=True)
    business_phone = models.CharField(max_length=50, blank=True)
    business_email = models.EmailField()
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    timezone = models.CharField(max_length=50, default='America/Chicago')
    currency = models.CharField(max_length=3, default='USD')

    is_active = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_in_trial(self):
        if not self.trial_ends_at:
            return False
        return timezone.now() < self.trial_ends_at

    def has_feature(self, feature_name):
        plan_features = settings.PLAN_FEATURES.get(self.plan, [])
        return feature_name in plan_features

    def can_add_vehicle(self):
        from apps.fleet.models import Vehicle
        current_count = Vehicle.objects.filter(tenant=self).count()
        return current_count < self.vehicle_limit

    def can_add_user(self):
        current_count = TenantUser.objects.filter(tenant=self).count()
        return current_count < self.user_limit

    def get_plan_limits(self):
        return settings.PLAN_LIMITS.get(self.plan, {})


class TenantUser(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['tenant', 'user']
        ordering = ['tenant', 'user']

    def __str__(self):
        return f'{self.user.username} @ {self.tenant.name}'

    def is_owner(self):
        return self.role == 'owner'

    def is_manager(self):
        return self.role == 'manager'

    def is_staff_member(self):
        return self.role == 'staff'

    def can_manage_vehicles(self):
        return self.role in ['owner', 'manager', 'staff']

    def can_manage_reservations(self):
        return self.role in ['owner', 'manager', 'staff']

    def can_manage_users(self):
        return self.role in ['owner', 'manager']

    def can_manage_settings(self):
        return self.role == 'owner'


class TenantModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TenantSettings(models.Model):
    """Tenant-specific settings including API keys and automation configuration."""

    MODEL_CHOICES = [
        ('anthropic/claude-3.5-sonnet', 'Claude 3.5 Sonnet (Recommended)'),
        ('anthropic/claude-3-opus', 'Claude 3 Opus'),
        ('openai/gpt-4-vision-preview', 'GPT-4 Vision'),
        ('google/gemini-pro-vision', 'Gemini Pro Vision'),
    ]

    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='settings'
    )

    # OpenRouter API Configuration
    openrouter_api_key_encrypted = models.BinaryField(blank=True, null=True)
    openrouter_enabled = models.BooleanField(default=False)
    openrouter_model = models.CharField(
        max_length=100,
        choices=MODEL_CHOICES,
        default='anthropic/claude-3.5-sonnet',
        help_text='Vision model to use for OCR'
    )

    # OCR Feature Toggles
    auto_parse_license = models.BooleanField(
        default=True,
        help_text='Automatically parse license images on upload'
    )
    auto_parse_insurance = models.BooleanField(
        default=True,
        help_text='Automatically parse insurance documents on upload'
    )

    # Rate limiting
    ocr_requests_today = models.IntegerField(default=0)
    ocr_requests_reset_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tenant Settings'
        verbose_name_plural = 'Tenant Settings'

    def __str__(self):
        return f'Settings for {self.tenant.name}'

    @property
    def has_api_key(self):
        """Check if an API key is configured (without exposing it)."""
        return bool(self.openrouter_api_key_encrypted)

    def get_api_key(self):
        """Decrypt and return the API key."""
        if not self.openrouter_api_key_encrypted:
            return None
        from apps.automation.ocr.utils.encryption import decrypt_api_key
        return decrypt_api_key(bytes(self.openrouter_api_key_encrypted))

    def set_api_key(self, api_key):
        """Encrypt and store the API key."""
        if not api_key:
            self.openrouter_api_key_encrypted = None
        else:
            from apps.automation.ocr.utils.encryption import encrypt_api_key
            self.openrouter_api_key_encrypted = encrypt_api_key(api_key)

    def can_make_ocr_request(self):
        """Check if tenant can make another OCR request (rate limiting)."""
        from datetime import date
        today = date.today()

        # Reset counter if it's a new day
        if self.ocr_requests_reset_at != today:
            self.ocr_requests_today = 0
            self.ocr_requests_reset_at = today
            self.save(update_fields=['ocr_requests_today', 'ocr_requests_reset_at'])

        # Limit: 100 requests per day
        return self.ocr_requests_today < 100

    def increment_ocr_requests(self):
        """Increment the OCR request counter."""
        self.ocr_requests_today += 1
        self.save(update_fields=['ocr_requests_today'])


class AuditMixin(models.Model):
    """Mixin to add audit fields to models."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
    )

    class Meta:
        abstract = True


class ActivityLog(models.Model):
    """Track all user actions in the system for audit purposes."""

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('upload', 'Upload'),
        ('checkout', 'Checkout'),
        ('checkin', 'Check-in'),
        ('status_change', 'Status Change'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f'{self.action} {self.model_name} #{self.object_id} by {self.user}'


def log_activity(tenant, user, action, instance, changes=None, ip_address=None):
    """Helper function to create an activity log entry."""
    return ActivityLog.objects.create(
        tenant=tenant,
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance)[:255],
        changes=changes,
        ip_address=ip_address,
    )
