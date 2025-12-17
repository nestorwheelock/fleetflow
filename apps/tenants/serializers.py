from rest_framework import serializers
from .models import Tenant, TenantUser


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
