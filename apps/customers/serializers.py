from rest_framework import serializers
from apps.tenants.utils import get_tenant_from_request
from .models import Customer, CustomerDocument


class CustomerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDocument
        fields = ['id', 'document_type', 'file', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    is_eligible = serializers.SerializerMethodField()
    total_rentals = serializers.IntegerField(read_only=True)
    documents = CustomerDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'phone_secondary', 'address', 'city', 'state', 'zip_code', 'country',
            'date_of_birth', 'age', 'license_number', 'license_state',
            'license_expiry', 'is_blacklisted', 'blacklist_reason', 'notes',
            'is_eligible', 'total_rentals', 'documents', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_eligible(self, obj):
        return obj.is_eligible_to_rent()

    def create(self, validated_data):
        tenant = get_tenant_from_request(self.context['request'])
        if not tenant:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('No tenant associated with request')
        validated_data['tenant'] = tenant
        return super().create(validated_data)


class CustomerListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    is_eligible = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'is_blacklisted', 'is_eligible',
        ]

    def get_is_eligible(self, obj):
        return obj.is_eligible_to_rent()
