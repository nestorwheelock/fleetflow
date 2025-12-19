from django.contrib import admin
from .models import LeadCapture, ReferralCredit


@admin.register(LeadCapture)
class LeadCaptureAdmin(admin.ModelAdmin):
    list_display = ['email', 'lead_type', 'source', 'converted', 'created_at']
    list_filter = ['lead_type', 'source', 'converted', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ReferralCredit)
class ReferralCreditAdmin(admin.ModelAdmin):
    list_display = [
        'referrer_email', 'referred_email', 'referral_type',
        'credit_amount', 'referrer_credited', 'referred_credited', 'created_at'
    ]
    list_filter = ['referral_type', 'referrer_credited', 'referred_credited', 'created_at']
    search_fields = ['referrer_email', 'referred_email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
