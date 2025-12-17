from rest_framework import serializers
from apps.tenants.utils import get_tenant_from_request
from .models import Vehicle, VehicleCategory, VehiclePhoto


class VehiclePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhoto
        fields = ['id', 'image', 'is_primary', 'caption', 'created_at']
        read_only_fields = ['id', 'created_at']


class VehicleCategorySerializer(serializers.ModelSerializer):
    vehicle_count = serializers.SerializerMethodField()

    class Meta:
        model = VehicleCategory
        fields = ['id', 'name', 'description', 'vehicle_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_vehicle_count(self, obj):
        return obj.vehicles.count()


class VehicleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    photos = VehiclePhotoSerializer(many=True, read_only=True)
    primary_photo = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'category', 'category_name', 'make', 'model', 'year',
            'license_plate', 'vin', 'color', 'status', 'daily_rate',
            'weekly_rate', 'monthly_rate', 'mileage', 'seats', 'doors',
            'transmission', 'fuel_type', 'features', 'notes',
            'insurance_policy', 'insurance_expiry', 'registration_expiry',
            'photos', 'primary_photo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_primary_photo(self, obj):
        photo = obj.photos.filter(is_primary=True).first()
        if photo and photo.image:
            return self.context['request'].build_absolute_uri(photo.image.url)
        return None

    def create(self, validated_data):
        tenant = get_tenant_from_request(self.context['request'])
        if not tenant:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('No tenant associated with request')
        validated_data['tenant'] = tenant
        return super().create(validated_data)


class VehicleListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_photo = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'make', 'model', 'year', 'license_plate', 'status',
            'daily_rate', 'category_name', 'primary_photo',
        ]

    def get_primary_photo(self, obj):
        photo = obj.photos.filter(is_primary=True).first()
        if photo and photo.image:
            return self.context['request'].build_absolute_uri(photo.image.url)
        return None
