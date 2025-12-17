from django.contrib import admin
from .models import Contract, ConditionReport, ConditionReportPhoto


class ConditionReportInline(admin.TabularInline):
    model = ConditionReport
    extra = 0


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'reservation', 'status', 'tenant', 'created_at']
    list_filter = ['status', 'tenant']
    search_fields = ['contract_number', 'reservation__customer__first_name', 'reservation__customer__last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ConditionReportInline]


class ConditionReportPhotoInline(admin.TabularInline):
    model = ConditionReportPhoto
    extra = 1


@admin.register(ConditionReport)
class ConditionReportAdmin(admin.ModelAdmin):
    list_display = ['contract', 'report_type', 'fuel_level', 'mileage', 'created_at']
    list_filter = ['report_type', 'fuel_level']
    inlines = [ConditionReportPhotoInline]
