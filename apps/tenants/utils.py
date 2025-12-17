def get_tenant_from_request(request):
    """
    Get tenant from request object.
    First tries request.tenant (set by middleware),
    then falls back to looking up via TenantUser.
    """
    if hasattr(request, 'tenant') and request.tenant:
        return request.tenant

    from apps.tenants.models import TenantUser
    if hasattr(request, 'user') and request.user.is_authenticated:
        tenant_user = TenantUser.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('tenant').first()
        if tenant_user:
            return tenant_user.tenant

    return None
