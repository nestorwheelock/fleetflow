from rest_framework import serializers
from .models import Tenant, TenantUser, TenantSettings


class TenantSerializer(serializers.ModelSerializer):
    vehicle_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'plan', 'business_name', 'business_address',
            'business_phone', 'business_email', 'logo', 'timezone', 'currency',
            'is_active', 'vehicle_limit', 'user_limit', 'vehicle_count', 'user_count',
            'subscription_status', 'trial_ends_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'plan', 'subscription_status', 'vehicle_limit',
            'user_limit', 'trial_ends_at', 'created_at', 'updated_at',
        ]

    def get_vehicle_count(self, obj):
        from apps.fleet.models import Vehicle
        return Vehicle.objects.filter(tenant=obj).count()

    def get_user_count(self, obj):
        return TenantUser.objects.filter(tenant=obj).count()


class TenantUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = TenantUser
        fields = ['id', 'user', 'username', 'email', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TenantStatsSerializer(serializers.Serializer):
    vehicle_count = serializers.IntegerField()
    customer_count = serializers.IntegerField()
    reservation_count = serializers.IntegerField()
    active_rentals = serializers.IntegerField()
    revenue_this_month = serializers.DecimalField(max_digits=10, decimal_places=2)


class TenantSettingsSerializer(serializers.ModelSerializer):
    has_api_key = serializers.BooleanField(read_only=True)
    api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    ocr_requests_today = serializers.IntegerField(read_only=True)
    can_use_ocr = serializers.SerializerMethodField()

    class Meta:
        model = TenantSettings
        fields = [
            'openrouter_enabled',
            'openrouter_model',
            'auto_parse_license',
            'auto_parse_insurance',
            'has_api_key',
            'api_key',
            'ocr_requests_today',
            'can_use_ocr',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'ocr_requests_today']

    def get_can_use_ocr(self, obj):
        from apps.automation.integration.feature_check import check_ocr_access
        return check_ocr_access(obj.tenant)

    def update(self, instance, validated_data):
        api_key = validated_data.pop('api_key', None)
        if api_key is not None:
            if api_key == '':
                instance.set_api_key(None)
            else:
                instance.set_api_key(api_key)
        return super().update(instance, validated_data)


class TenantSettingsUpdateSerializer(serializers.Serializer):
    openrouter_enabled = serializers.BooleanField(required=False)
    openrouter_model = serializers.ChoiceField(
        choices=TenantSettings.MODEL_CHOICES,
        required=False
    )
    auto_parse_license = serializers.BooleanField(required=False)
    auto_parse_insurance = serializers.BooleanField(required=False)
    api_key = serializers.CharField(required=False, allow_blank=True)
