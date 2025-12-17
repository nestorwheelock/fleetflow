from django.db import models
from django.conf import settings
from django.utils import timezone


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
