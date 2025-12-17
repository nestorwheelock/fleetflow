from django.db import models
from django.utils import timezone
from io import BytesIO

from apps.tenants.models import TenantModel
from apps.reservations.models import Reservation


class Contract(TenantModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_signature', 'Pending Signature'),
        ('signed', 'Signed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='contract'
    )
    contract_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    terms_and_conditions = models.TextField(blank=True)

    customer_signature = models.TextField(blank=True)
    customer_signed_at = models.DateTimeField(null=True, blank=True)
    staff_signature = models.TextField(blank=True)
    staff_signed_at = models.DateTimeField(null=True, blank=True)

    pdf_file = models.FileField(upload_to='contracts/', blank=True, null=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['tenant', 'contract_number']
        ordering = ['-created_at']

    def __str__(self):
        return self.contract_number or f'Contract #{self.pk}'

    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = self.generate_contract_number()
        super().save(*args, **kwargs)

    def generate_contract_number(self):
        year = timezone.now().year
        last_contract = Contract.objects.filter(
            tenant=self.tenant,
            contract_number__startswith=f'CTR-{year}-'
        ).order_by('-contract_number').first()

        if last_contract:
            try:
                last_num = int(last_contract.contract_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1

        return f'CTR-{year}-{new_num:04d}'

    def sign(self, signature, is_customer=True):
        if is_customer:
            self.customer_signature = signature
            self.customer_signed_at = timezone.now()
        else:
            self.staff_signature = signature
            self.staff_signed_at = timezone.now()

        if self.customer_signature and self.status == 'pending_signature':
            self.status = 'signed'

        self.save()

    def generate_pdf(self):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10
        )
        normal_style = styles['Normal']

        story = []

        story.append(Paragraph(self.tenant.business_name, title_style))
        story.append(Paragraph("RENTAL AGREEMENT", title_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"Contract #: {self.contract_number}", normal_style))
        story.append(Paragraph(f"Date: {self.created_at.strftime('%B %d, %Y')}", normal_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph("CUSTOMER INFORMATION", heading_style))
        customer = self.reservation.customer
        customer_info = [
            ['Name:', customer.full_name],
            ['Email:', customer.email],
            ['Phone:', customer.phone],
            ['Address:', customer.address or 'N/A'],
            ['License #:', customer.license_number or 'N/A'],
        ]
        t = Table(customer_info, colWidths=[1.5*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        story.append(Paragraph("VEHICLE INFORMATION", heading_style))
        vehicle = self.reservation.vehicle
        vehicle_info = [
            ['Vehicle:', str(vehicle)],
            ['VIN:', vehicle.vin],
            ['Color:', vehicle.color or 'N/A'],
            ['Mileage:', f'{vehicle.mileage:,} miles'],
        ]
        t = Table(vehicle_info, colWidths=[1.5*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        story.append(Paragraph("RENTAL DETAILS", heading_style))
        reservation = self.reservation
        rental_info = [
            ['Pickup Date:', reservation.start_date.strftime('%B %d, %Y')],
            ['Return Date:', reservation.end_date.strftime('%B %d, %Y')],
            ['Duration:', f'{reservation.duration_days} days'],
            ['Daily Rate:', f'${reservation.daily_rate:.2f}'],
            ['Total Amount:', f'${reservation.total_amount:.2f}'],
        ]
        t = Table(rental_info, colWidths=[1.5*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        if self.terms_and_conditions:
            story.append(Paragraph("TERMS AND CONDITIONS", heading_style))
            story.append(Paragraph(self.terms_and_conditions, normal_style))
            story.append(Spacer(1, 15))

        story.append(Paragraph("SIGNATURES", heading_style))
        story.append(Spacer(1, 30))

        sig_data = [
            ['_' * 40, '', '_' * 40],
            ['Customer Signature', '', 'Staff Signature'],
            ['', '', ''],
            ['Date: _________________', '', 'Date: _________________'],
        ]
        sig_table = Table(sig_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(sig_table)

        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"{self.tenant.business_name} | {self.tenant.business_phone} | {self.tenant.business_email}",
            ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=1)
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


class ConditionReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('checkout', 'Check-out'),
        ('checkin', 'Check-in'),
    ]

    FUEL_LEVEL_CHOICES = [
        ('empty', 'Empty'),
        ('1/4', '1/4'),
        ('1/2', '1/2'),
        ('3/4', '3/4'),
        ('full', 'Full'),
    ]

    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='condition_reports'
    )
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)

    fuel_level = models.CharField(max_length=10, choices=FUEL_LEVEL_CHOICES)
    mileage = models.PositiveIntegerField()

    exterior_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    interior_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)

    damages = models.JSONField(default=list, blank=True)

    notes = models.TextField(blank=True)

    inspector_name = models.CharField(max_length=100, blank=True)
    customer_acknowledged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_report_type_display()} - {self.contract}'


class ConditionReportPhoto(models.Model):
    LOCATION_CHOICES = [
        ('front', 'Front'),
        ('back', 'Back'),
        ('left', 'Left Side'),
        ('right', 'Right Side'),
        ('interior', 'Interior'),
        ('dashboard', 'Dashboard'),
        ('trunk', 'Trunk'),
        ('damage', 'Damage Detail'),
        ('other', 'Other'),
    ]

    condition_report = models.ForeignKey(
        ConditionReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    image = models.ImageField(upload_to='condition_reports/')
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['location', 'created_at']

    def __str__(self):
        return f'{self.get_location_display()} - {self.condition_report}'
