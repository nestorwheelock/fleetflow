def tenant_context(request):
    tenant = getattr(request, 'tenant', None)
    tenant_user = getattr(request, 'tenant_user', None)
    branding = None
    branding_css = ''

    if tenant:
        try:
            branding = tenant.branding
        except Exception:
            branding = None

        if branding:
            css_vars = branding.get_css_variables()
            branding_css = '; '.join([f'{k}: {v}' for k, v in css_vars.items()])

    return {
        'tenant': tenant,
        'tenant_user': tenant_user,
        'branding': branding,
        'branding_css': branding_css,
    }
