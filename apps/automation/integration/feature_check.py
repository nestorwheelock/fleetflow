from django.conf import settings


def tenant_has_feature(tenant, feature):
    """Check if tenant's plan includes a specific feature."""
    plan_features = settings.PLAN_FEATURES.get(tenant.plan, [])
    return feature in plan_features


def check_ocr_access(tenant):
    """Check if tenant can use OCR features.

    Requires:
    1. Plan includes license_ocr or insurance_ocr feature
    2. Tenant has settings with openrouter_enabled=True
    """
    if not tenant_has_feature(tenant, 'license_ocr'):
        return False

    if hasattr(tenant, 'settings') and tenant.settings.openrouter_enabled:
        return tenant.settings.has_api_key

    return False
