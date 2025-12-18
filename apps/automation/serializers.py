from rest_framework import serializers
from apps.customers.models import Customer, CustomerInsurance


class LicenseParseRequestSerializer(serializers.Serializer):
    """Request serializer for license parsing."""
    customer_id = serializers.IntegerField(required=False)
    image = serializers.ImageField(required=False)


class LicenseDataSerializer(serializers.Serializer):
    """Serializer for parsed license data."""
    country = serializers.CharField(allow_blank=True, default='')
    issuing_authority = serializers.CharField(allow_blank=True, default='')
    license_number = serializers.CharField(allow_blank=True, default='')
    license_class = serializers.CharField(allow_blank=True, default='')
    issue_date = serializers.DateField(allow_null=True, required=False)
    expiration_date = serializers.DateField(allow_null=True, required=False)
    first_name = serializers.CharField(allow_blank=True, default='')
    middle_name = serializers.CharField(allow_blank=True, default='')
    last_name = serializers.CharField(allow_blank=True, default='')
    date_of_birth = serializers.DateField(allow_null=True, required=False)
    address_street = serializers.CharField(allow_blank=True, default='')
    address_city = serializers.CharField(allow_blank=True, default='')
    address_state = serializers.CharField(allow_blank=True, default='')
    address_zip = serializers.CharField(allow_blank=True, default='')
    gender = serializers.CharField(allow_blank=True, default='')
    height = serializers.CharField(allow_blank=True, default='')
    weight = serializers.CharField(allow_blank=True, default='')
    eye_color = serializers.CharField(allow_blank=True, default='')
    hair_color = serializers.CharField(allow_blank=True, default='')
    restrictions = serializers.CharField(allow_blank=True, default='')
    endorsements = serializers.CharField(allow_blank=True, default='')
    donor_status = serializers.BooleanField(allow_null=True, required=False)
    confidence = serializers.FloatField(default=0.0)
    has_photo = serializers.BooleanField(default=False)


class InsuranceParseRequestSerializer(serializers.Serializer):
    """Request serializer for insurance parsing."""
    customer_id = serializers.IntegerField(required=False)
    image = serializers.ImageField(required=False)


class InsuranceDataSerializer(serializers.Serializer):
    """Serializer for parsed insurance data."""
    company_name = serializers.CharField(allow_blank=True, default='')
    policy_number = serializers.CharField(allow_blank=True, default='')
    group_number = serializers.CharField(allow_blank=True, default='')
    effective_date = serializers.DateField(allow_null=True, required=False)
    expiration_date = serializers.DateField(allow_null=True, required=False)
    policyholder_name = serializers.CharField(allow_blank=True, default='')
    policyholder_relationship = serializers.CharField(allow_blank=True, default='')
    coverage_type = serializers.CharField(allow_blank=True, default='')
    covered_vehicles = serializers.ListField(child=serializers.DictField(), default=list)
    agent_name = serializers.CharField(allow_blank=True, default='')
    agent_phone = serializers.CharField(allow_blank=True, default='')
    confidence = serializers.FloatField(default=0.0)


class ApplyLicenseDataSerializer(serializers.Serializer):
    """Serializer for applying parsed license data to a customer."""
    fields = serializers.ListField(
        child=serializers.CharField(),
        help_text='List of field names to apply'
    )
    data = LicenseDataSerializer()


class ApplyInsuranceDataSerializer(serializers.Serializer):
    """Serializer for applying parsed insurance data."""
    data = InsuranceDataSerializer()
