from django.contrib import admin
from .models import Customer, CustomerDocument


class CustomerDocumentInline(admin.TabularInline):
    model = CustomerDocument
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'is_blacklisted', 'tenant']
    list_filter = ['is_blacklisted', 'tenant']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'license_number']
    inlines = [CustomerDocumentInline]
    readonly_fields = ['created_at', 'updated_at']
