from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Tenant, TenantUser, User, TenantSettings, ActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model with email as username."""

    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_customer', 'email_verified']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_customer', 'email_verified']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer', 'groups', 'user_permissions'),
        }),
        (_('Email verification'), {'fields': ('email_verified', 'email_verified_at')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['email_verified_at', 'last_login', 'date_joined']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'subscription_status']
    search_fields = ['name', 'slug', 'business_name', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'tenant']
    search_fields = ['user__email', 'tenant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'openrouter_enabled', 'auto_parse_license', 'auto_parse_insurance']
    list_filter = ['openrouter_enabled', 'auto_parse_license', 'auto_parse_insurance']
    search_fields = ['tenant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'tenant', 'user', 'action', 'model_name', 'object_repr']
    list_filter = ['action', 'model_name', 'tenant']
    search_fields = ['user__email', 'object_repr', 'tenant__name']
    readonly_fields = ['tenant', 'user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
