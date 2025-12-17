# T-020: PDF Generation with ReportLab

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Generate PDF rental contracts and receipts
**Related Story**: S-005 (Basic Contract Generation)

## Constraints
**Allowed File Paths**:
- /apps/contracts/pdf.py
- /apps/contracts/services.py
- /requirements/*.txt

## Deliverables
- [ ] ReportLab integration
- [ ] Contract PDF template
- [ ] Receipt PDF template
- [ ] Signature embedding
- [ ] PDF storage and retrieval

## Technical Specifications

### Dependencies
```
# requirements/base.txt
reportlab>=4.0.0
Pillow>=10.0.0
```

### PDF Generator Service
```python
# apps/contracts/pdf.py

from io import BytesIO
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import base64

class ContractPDFGenerator:
    def __init__(self, contract):
        self.contract = contract
        self.reservation = contract.reservation
        self.customer = self.reservation.customer
        self.vehicle = self.reservation.vehicle
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='ContractTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey
        ))
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=2
        ))

    def generate(self):
        """Generate the contract PDF and return as bytes."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # Header
        story.extend(self._build_header())

        # Contract info section
        story.extend(self._build_contract_info())

        # Renter information
        story.extend(self._build_renter_section())

        # Vehicle information
        story.extend(self._build_vehicle_section())

        # Rental period
        story.extend(self._build_rental_period())

        # Charges
        story.extend(self._build_charges_section())

        # Terms and conditions
        story.extend(self._build_terms_section())

        # Signature section
        story.extend(self._build_signature_section())

        doc.build(story)
        return buffer.getvalue()

    def _build_header(self):
        """Build document header."""
        elements = []

        # Company name/logo
        elements.append(Paragraph(
            "FLEETFLOW CAR RENTAL",
            self.styles['ContractTitle']
        ))
        elements.append(Paragraph(
            "RENTAL AGREEMENT",
            self.styles['Heading2']
        ))
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.black,
            spaceAfter=20
        ))

        return elements

    def _build_contract_info(self):
        """Build contract reference section."""
        elements = []

        data = [
            ['Contract #:', self.contract.contract_number,
             'Date:', self.contract.created_at.strftime('%B %d, %Y')],
            ['Reservation #:', self.reservation.confirmation_number,
             'Status:', self.contract.get_status_display()],
        ]

        table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_renter_section(self):
        """Build renter information section."""
        elements = []

        elements.append(Paragraph("RENTER INFORMATION", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        data = [
            ['Name:', self.customer.full_name],
            ['Address:', self.customer.full_address],
            ['Phone:', self.customer.phone],
            ['Email:', self.customer.email],
            ['License #:', f"{self.customer.license_number} ({self.customer.license_state})"],
            ['License Exp:', self.customer.license_expiry.strftime('%m/%d/%Y') if self.customer.license_expiry else 'N/A'],
        ]

        table = Table(data, colWidths=[1.5*inch, 5*inch])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        return elements

    def _build_vehicle_section(self):
        """Build vehicle information section."""
        elements = []

        elements.append(Paragraph("VEHICLE INFORMATION", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        data = [
            ['Vehicle:', f"{self.vehicle.year} {self.vehicle.make} {self.vehicle.model}"],
            ['VIN:', self.vehicle.vin],
            ['License Plate:', self.vehicle.license_plate],
            ['Color:', self.vehicle.color],
            ['Mileage at Pickup:', f"{self.reservation.pickup_mileage:,} miles" if self.reservation.pickup_mileage else 'TBD'],
        ]

        table = Table(data, colWidths=[1.5*inch, 5*inch])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        return elements

    def _build_rental_period(self):
        """Build rental period section."""
        elements = []

        elements.append(Paragraph("RENTAL PERIOD", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        pickup_dt = f"{self.reservation.pickup_date.strftime('%B %d, %Y')} at {self.reservation.pickup_time.strftime('%I:%M %p')}"
        return_dt = f"{self.reservation.return_date.strftime('%B %d, %Y')} at {self.reservation.return_time.strftime('%I:%M %p')}"

        data = [
            ['Pickup:', pickup_dt],
            ['Return:', return_dt],
            ['Duration:', f"{self.reservation.duration_days} days"],
        ]

        table = Table(data, colWidths=[1.5*inch, 5*inch])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        return elements

    def _build_charges_section(self):
        """Build charges breakdown section."""
        elements = []

        elements.append(Paragraph("CHARGES", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        data = [
            ['Daily Rate:', f"${self.reservation.daily_rate} × {self.reservation.duration_days} days",
             f"${self.reservation.subtotal:.2f}"],
            ['Tax (8%):', '', f"${self.reservation.tax_amount:.2f}"],
            ['', '', ''],
            ['TOTAL:', '', f"${self.reservation.total_amount:.2f}"],
            ['', '', ''],
            ['Security Deposit:', '(Refundable)', f"${self.reservation.deposit_amount:.2f}"],
        ]

        table = Table(data, colWidths=[2*inch, 2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('LINEABOVE', (0, 3), (-1, 3), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        return elements

    def _build_terms_section(self):
        """Build terms and conditions section."""
        elements = []

        elements.append(Paragraph("TERMS AND CONDITIONS", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        # Split terms into paragraphs
        terms = self.contract.rental_terms.split('\n\n')
        for term in terms[:10]:  # Limit to first 10 paragraphs
            if term.strip():
                elements.append(Paragraph(term.strip(), self.styles['Normal']))
                elements.append(Spacer(1, 5))

        elements.append(Spacer(1, 15))

        return elements

    def _build_signature_section(self):
        """Build signature section."""
        elements = []

        elements.append(Paragraph("SIGNATURES", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        # Add signature image if available
        if self.contract.signature_data:
            try:
                # Decode base64 signature
                sig_data = self.contract.signature_data
                if sig_data.startswith('data:'):
                    sig_data = sig_data.split(',')[1]

                sig_bytes = base64.b64decode(sig_data)
                sig_buffer = BytesIO(sig_bytes)

                elements.append(Paragraph("Renter Signature:", self.styles['FieldLabel']))
                elements.append(Image(sig_buffer, width=3*inch, height=1*inch))
                elements.append(Paragraph(
                    f"Signed by: {self.contract.signer_name}",
                    self.styles['FieldValue']
                ))
                elements.append(Paragraph(
                    f"Date: {self.contract.signed_at.strftime('%B %d, %Y at %I:%M %p')}",
                    self.styles['FieldValue']
                ))
            except Exception:
                elements.append(Paragraph("_" * 40, self.styles['Normal']))
                elements.append(Paragraph("Renter Signature", self.styles['FieldLabel']))
        else:
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("_" * 40, self.styles['Normal']))
            elements.append(Paragraph("Renter Signature                    Date", self.styles['FieldLabel']))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("_" * 40, self.styles['Normal']))
        elements.append(Paragraph("Agent Signature                     Date", self.styles['FieldLabel']))

        return elements


class ReceiptPDFGenerator:
    """Generate receipt PDF for completed rentals."""

    def __init__(self, reservation):
        self.reservation = reservation
        self.customer = reservation.customer
        self.vehicle = reservation.vehicle
        self.styles = getSampleStyleSheet()

    def generate(self):
        """Generate receipt PDF."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        story = []

        # Header
        story.append(Paragraph("FLEETFLOW CAR RENTAL", self.styles['Heading1']))
        story.append(Paragraph("RENTAL RECEIPT", self.styles['Heading2']))
        story.append(Spacer(1, 20))

        # Receipt details
        story.append(Paragraph(f"Receipt #: {self.reservation.confirmation_number}", self.styles['Normal']))
        story.append(Paragraph(f"Date: {self.reservation.actual_return.strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Customer and vehicle info
        story.append(Paragraph(f"Customer: {self.customer.full_name}", self.styles['Normal']))
        story.append(Paragraph(f"Vehicle: {self.vehicle}", self.styles['Normal']))
        story.append(Paragraph(f"Period: {self.reservation.pickup_date} - {self.reservation.return_date}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Charges table
        story.append(Paragraph("CHARGES", self.styles['Heading3']))
        # ... similar charge breakdown ...

        story.append(Paragraph(f"TOTAL PAID: ${self.reservation.total_amount:.2f}", self.styles['Heading2']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("Thank you for choosing FleetFlow!", self.styles['Normal']))

        doc.build(story)
        return buffer.getvalue()
```

## Definition of Done
- [ ] ReportLab installed and configured
- [ ] Contract PDF generates correctly
- [ ] Receipt PDF generates correctly
- [ ] Signature embedded in PDF
- [ ] PDF stored with contract
- [ ] Tests written and passing (>95% coverage)
