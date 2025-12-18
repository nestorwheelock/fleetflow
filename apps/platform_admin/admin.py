from django.contrib import admin
from .models import PlatformSettings, ImpersonationLog, PlatformAuditLog


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ['platform_name', 'require_email_verification', 'allow_custom_domains', 'maintenance_mode', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Only allow one instance (singleton)
        return not PlatformSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ImpersonationLog)
class ImpersonationLogAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'target_user', 'tenant', 'started_at', 'ended_at', 'is_active']
    list_filter = ['started_at', 'tenant']
    search_fields = ['admin_user__email', 'target_user__email', 'reason']
    readonly_fields = ['admin_user', 'target_user', 'tenant', 'reason', 'started_at', 'ended_at', 'ip_address', 'user_agent']
    date_hierarchy = 'started_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PlatformAuditLog)
class PlatformAuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'admin_user', 'action', 'tenant', 'description']
    list_filter = ['action', 'timestamp', 'tenant']
    search_fields = ['admin_user__email', 'description', 'tenant__name']
    readonly_fields = ['admin_user', 'action', 'tenant', 'target_user', 'description', 'changes', 'ip_address', 'user_agent', 'timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
