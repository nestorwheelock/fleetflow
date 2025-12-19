from django.db import models


class LeadCapture(models.Model):
    """Email leads from landing page signups."""

    LEAD_TYPE_CHOICES = [
        ('owner', 'Has Cars to Rent'),
        ('renter', 'Looking for Rental'),
    ]

    email = models.EmailField(unique=True)
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES)
    source = models.CharField(max_length=50, default='homepage')
    created_at = models.DateTimeField(auto_now_add=True)
    converted = models.BooleanField(default=False)
    converted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self):
        return f"{self.email} ({self.get_lead_type_display()})"


class ReferralCredit(models.Model):
    """Track referral credits between users."""

    REFERRAL_TYPE_CHOICES = [
        ('owner', 'Has Cars to Rent'),
        ('renter', 'Looking for Rental'),
    ]

    referrer_email = models.EmailField()
    referred_email = models.EmailField()
    referral_type = models.CharField(max_length=20, choices=REFERRAL_TYPE_CHOICES)
    credit_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=25.00
    )
    referrer_credited = models.BooleanField(default=False)
    referred_credited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Referral Credit'
        verbose_name_plural = 'Referral Credits'

    def __str__(self):
        return f"{self.referrer_email} → {self.referred_email} (${self.credit_amount})"
