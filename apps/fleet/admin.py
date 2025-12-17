from django.contrib import admin
from .models import Vehicle, VehicleCategory, VehiclePhoto


class VehiclePhotoInline(admin.TabularInline):
    model = VehiclePhoto
    extra = 1


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'created_at']
    list_filter = ['tenant']
    search_fields = ['name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'year', 'license_plate', 'status', 'daily_rate', 'tenant']
    list_filter = ['status', 'tenant', 'category', 'make', 'transmission', 'fuel_type']
    search_fields = ['make', 'model', 'license_plate', 'vin']
    inlines = [VehiclePhotoInline]
    readonly_fields = ['created_at', 'updated_at']
