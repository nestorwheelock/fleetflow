class TenantViewMixin:
    def get_tenant(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return self.request.tenant
        from apps.tenants.models import TenantUser
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            tenant_user = TenantUser.objects.filter(
                user=self.request.user,
                is_active=True
            ).select_related('tenant').first()
            if tenant_user:
                return tenant_user.tenant
        return None

    def get_tenant_user(self):
        """Get the TenantUser for the current request user."""
        if hasattr(self.request, 'tenant_user') and self.request.tenant_user:
            return self.request.tenant_user
        from apps.tenants.models import TenantUser
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            tenant = self.get_tenant()
            if tenant:
                return TenantUser.objects.filter(
                    user=self.request.user,
                    tenant=tenant,
                    is_active=True
                ).first()
        return None
