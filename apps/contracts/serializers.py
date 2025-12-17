from rest_framework import serializers
from apps.tenants.utils import get_tenant_from_request
from .models import Contract, ConditionReport, ConditionReportPhoto


class ConditionReportPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionReportPhoto
        fields = ['id', 'image', 'location', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConditionReportSerializer(serializers.ModelSerializer):
    photos = ConditionReportPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = ConditionReport
        fields = [
            'id', 'report_type', 'fuel_level', 'mileage',
            'exterior_condition', 'interior_condition', 'damages',
            'notes', 'inspector_name', 'customer_acknowledged',
            'photos', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ContractSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='reservation.customer.full_name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()
    condition_reports = ConditionReportSerializer(many=True, read_only=True)
    is_signed = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'reservation', 'contract_number', 'status',
            'terms_and_conditions', 'customer_signed_at', 'staff_signed_at',
            'customer_name', 'vehicle_name', 'condition_reports',
            'is_signed', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'contract_number', 'customer_signed_at', 'staff_signed_at',
            'created_at', 'updated_at',
        ]

    def get_vehicle_name(self, obj):
        return str(obj.reservation.vehicle)

    def get_is_signed(self, obj):
        return bool(obj.customer_signature)

    def create(self, validated_data):
        tenant = get_tenant_from_request(self.context['request'])
        if not tenant:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('No tenant associated with request')
        validated_data['tenant'] = tenant
        return super().create(validated_data)


class ContractListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='reservation.customer.full_name', read_only=True)
    vehicle_name = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'status', 'customer_name',
            'vehicle_name', 'created_at',
        ]

    def get_vehicle_name(self, obj):
        return str(obj.reservation.vehicle)


class SignatureSerializer(serializers.Serializer):
    signature = serializers.CharField(required=True)
    is_customer = serializers.BooleanField(default=True)
