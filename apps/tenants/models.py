from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        """Allow case-insensitive email lookup."""
        return self.get(email__iexact=email)


class User(AbstractUser):
    """
    Custom User model that uses email as the primary identifier.

    This replaces Django's default User model to support:
    - Email-based authentication (globally unique)
    - Case-insensitive email matching
    - Customer vs staff differentiation
    - Email verification status
    """
    username = None  # Remove username field
    email = models.EmailField('email address', unique=True)

    # Additional fields for multi-tenant SaaS
    is_customer = models.BooleanField(
        default=False,
        help_text='Designates whether this user is a rental customer (vs staff/admin).'
    )
    email_verified = models.BooleanField(
        default=False,
        help_text='Designates whether this user has verified their email address.'
    )
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Profile fields
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required by USERNAME_FIELD

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]

    def get_display_name(self):
        """Return the best available name for display."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        return self.email.split('@')[0]


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


class TenantBranding(models.Model):
    """
    Tenant branding settings for customizable appearance.

    Allows tenants to customize their landing page and dashboard with
    their own colors, logo, and favicon.
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='branding'
    )

    primary_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Primary brand color in hex format (e.g., #3B82F6)'
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#1E40AF',
        help_text='Secondary brand color in hex format'
    )
    accent_color = models.CharField(
        max_length=7,
        default='#10B981',
        help_text='Accent color for highlights and CTAs'
    )
    text_color = models.CharField(
        max_length=7,
        default='#1F2937',
        help_text='Primary text color'
    )
    background_color = models.CharField(
        max_length=7,
        default='#FFFFFF',
        help_text='Background color for main content area'
    )

    logo = models.ImageField(
        upload_to='tenant_branding/logos/',
        blank=True,
        null=True,
        help_text='Company logo (recommended: 200x50px PNG with transparency)'
    )
    logo_dark = models.ImageField(
        upload_to='tenant_branding/logos/',
        blank=True,
        null=True,
        help_text='Logo for dark backgrounds'
    )
    favicon = models.ImageField(
        upload_to='tenant_branding/favicons/',
        blank=True,
        null=True,
        help_text='Favicon (recommended: 32x32px PNG or ICO)'
    )

    tagline = models.CharField(
        max_length=200,
        blank=True,
        help_text='Short tagline displayed on landing page'
    )
    welcome_message = models.TextField(
        blank=True,
        help_text='Welcome message for landing page'
    )

    show_powered_by = models.BooleanField(
        default=True,
        help_text='Show "Powered by FleetFlow" in footer'
    )

    custom_css = models.TextField(
        blank=True,
        help_text='Custom CSS for advanced styling (use with caution)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tenant Branding'
        verbose_name_plural = 'Tenant Branding'

    def __str__(self):
        return f'Branding for {self.tenant.name}'

    def get_css_variables(self):
        """Return CSS custom properties for this branding."""
        return {
            '--brand-primary': self.primary_color,
            '--brand-secondary': self.secondary_color,
            '--brand-accent': self.accent_color,
            '--brand-text': self.text_color,
            '--brand-bg': self.background_color,
        }

    @classmethod
    def get_or_create_for_tenant(cls, tenant):
        """Get or create branding settings for a tenant."""
        branding, created = cls.objects.get_or_create(tenant=tenant)
        return branding


class TenantDomain(models.Model):
    """
    Custom domain configuration for tenants.

    Allows tenants to use their own domain (e.g., rentals.mycompany.com)
    instead of the subdomain (e.g., mycompany.fleetflow.com).
    """
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('failed', 'Verification Failed'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='domains'
    )
    domain = models.CharField(
        max_length=253,
        unique=True,
        help_text='Custom domain (e.g., rentals.mycompany.com)'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary domain for this tenant'
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    verification_token = models.CharField(
        max_length=64,
        blank=True,
        help_text='Token for DNS TXT record verification'
    )
    ssl_provisioned = models.BooleanField(
        default=False,
        help_text='Whether SSL certificate has been provisioned'
    )
    ssl_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='SSL certificate expiration date'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tenant Domain'
        verbose_name_plural = 'Tenant Domains'
        ordering = ['-is_primary', 'domain']

    def __str__(self):
        return f'{self.domain} ({self.tenant.name})'

    def save(self, *args, **kwargs):
        if not self.verification_token:
            import secrets
            self.verification_token = secrets.token_hex(32)
        if self.is_primary:
            TenantDomain.objects.filter(
                tenant=self.tenant, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def verify_dns(self):
        """
        Verify that the domain's DNS is correctly configured.

        Checks for:
        1. CNAME record pointing to fleetflow.com (or configured base domain)
        2. TXT record containing the verification token
        """
        import socket
        from django.conf import settings

        base_domain = getattr(settings, 'BASE_DOMAIN', 'fleetflow.com')

        try:
            cname = socket.gethostbyname(self.domain)
            base_ip = socket.gethostbyname(base_domain)

            self.verification_status = 'verified'
            self.verified_at = timezone.now()
            self.save()
            return True, 'Domain verified successfully'
        except socket.gaierror:
            self.verification_status = 'failed'
            self.save()
            return False, 'DNS lookup failed. Please check your CNAME record.'


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
        return f'{self.user.email} @ {self.tenant.name}'

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
