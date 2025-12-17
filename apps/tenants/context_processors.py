def tenant_context(request):
    return {
        'tenant': getattr(request, 'tenant', None),
        'tenant_user': getattr(request, 'tenant_user', None),
    }
