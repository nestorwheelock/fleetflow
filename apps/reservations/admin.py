from django.contrib import admin
from .models import Reservation, ReservationExtra


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'vehicle', 'start_date', 'end_date',
        'status', 'total_amount', 'tenant'
    ]
    list_filter = ['status', 'tenant', 'start_date']
    search_fields = [
        'customer__first_name', 'customer__last_name',
        'vehicle__license_plate', 'vehicle__make', 'vehicle__model'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(ReservationExtra)
class ReservationExtraAdmin(admin.ModelAdmin):
    list_display = ['name', 'daily_price', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name']
