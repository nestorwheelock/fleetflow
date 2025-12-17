# T-021: Contract Storage and Retrieval

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement contract storage, retrieval, and viewing
**Related Story**: S-005 (Basic Contract Generation)

## Constraints
**Allowed File Paths**:
- /apps/contracts/views.py
- /apps/contracts/urls.py
- /apps/contracts/services.py
- /templates/contracts/*

## Deliverables
- [ ] Contract service layer
- [ ] Contract generation on checkout
- [ ] Contract viewing page
- [ ] Contract download (PDF)
- [ ] Contract print view
- [ ] Contract listing for reservation

## Technical Specifications

### Contract Service
```python
# apps/contracts/services.py

from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Contract, TermsAndConditions
from .pdf import ContractPDFGenerator, ReceiptPDFGenerator

class ContractService:
    @classmethod
    def create_contract(cls, reservation, created_by=None):
        """Create a new contract for a reservation."""
        terms = TermsAndConditions.get_current()

        contract = Contract.objects.create(
            reservation=reservation,
            terms_version=terms.version if terms else '1.0',
            rental_terms=terms.content if terms else cls._get_default_terms(),
            daily_rate_snapshot=reservation.daily_rate,
            total_amount_snapshot=reservation.total_amount,
            status='draft',
            created_by=created_by
        )

        return contract

    @classmethod
    def generate_contract(cls, reservation, signature_data=None, ip_address=None, user_agent=None):
        """Generate and finalize contract with optional signature."""
        # Get or create contract
        contract = reservation.contracts.filter(status__in=['draft', 'pending_signature']).first()
        if not contract:
            contract = cls.create_contract(reservation)

        # Add signature if provided
        if signature_data:
            contract.mark_signed(signature_data, ip_address, user_agent)

        # Generate PDF
        pdf_generator = ContractPDFGenerator(contract)
        pdf_content = pdf_generator.generate()

        # Save PDF to contract
        filename = f"contract_{contract.contract_number}.pdf"
        contract.document_pdf.save(filename, ContentFile(pdf_content))

        return contract

    @classmethod
    def generate_receipt(cls, reservation):
        """Generate receipt PDF for completed rental."""
        pdf_generator = ReceiptPDFGenerator(reservation)
        pdf_content = pdf_generator.generate()

        # Store receipt (could be separate model or attached to reservation)
        filename = f"receipt_{reservation.confirmation_number}.pdf"

        # Save to reservation or return bytes
        return pdf_content, filename

    @classmethod
    def void_contract(cls, contract, reason=''):
        """Void a contract."""
        contract.status = 'voided'
        if reason:
            contract.special_conditions += f"\n\nVOIDED: {reason}"
        contract.save()
        return contract

    @staticmethod
    def _get_default_terms():
        """Return default terms if none configured."""
        return """
RENTAL AGREEMENT TERMS AND CONDITIONS

1. RENTAL PERIOD
The rental period begins at the pickup date and time specified and ends at the
return date and time specified. Late returns will incur additional charges.

2. MILEAGE
Your rental includes 150 miles per day. Additional miles will be charged at
$0.25 per mile.

3. FUEL POLICY
The vehicle is provided with a full tank of fuel and must be returned with a
full tank. If returned with less fuel, you will be charged $4.50 per gallon
plus a refueling service fee.

4. INSURANCE AND LIABILITY
You are responsible for all damages to the vehicle during the rental period.
Optional insurance coverage is available to limit your liability.

5. PROHIBITED USES
The vehicle may not be used for off-road driving, racing, towing, transporting
hazardous materials, illegal activities, or subleasing to others.

6. ACCIDENTS AND DAMAGE
In case of accident, contact local authorities if required, do not admit fault,
and contact our office immediately.

By signing this agreement, I acknowledge that I have read and agree to all
terms and conditions stated above.
"""
```

### Contract Views
```python
# apps/contracts/views.py

from django.views.generic import DetailView, ListView, View
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Contract
from .services import ContractService

class ContractDetailView(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = self.object.reservation
        context['can_sign'] = self.object.status == 'pending_signature'
        return context


class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by reservation if provided
        reservation_id = self.request.GET.get('reservation')
        if reservation_id:
            queryset = queryset.filter(reservation_id=reservation_id)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.select_related('reservation', 'reservation__customer')


class ContractDownloadView(LoginRequiredMixin, View):
    """Download contract PDF."""

    def get(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)

        # Generate PDF if not exists
        if not contract.document_pdf:
            ContractService.generate_contract(contract.reservation)
            contract.refresh_from_db()

        if contract.document_pdf:
            response = FileResponse(
                contract.document_pdf.open('rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{contract.contract_number}.pdf"'
            return response

        return HttpResponse("Contract PDF not available", status=404)


class ContractPrintView(LoginRequiredMixin, DetailView):
    """Print-friendly contract view."""
    model = Contract
    template_name = 'contracts/contract_print.html'
    context_object_name = 'contract'


class ContractSignView(LoginRequiredMixin, View):
    """Handle contract signing."""

    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk, status='pending_signature')

        signature_data = request.POST.get('signature_data')
        if not signature_data:
            return HttpResponse("Signature required", status=400)

        # Get client info
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or \
                     request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Sign and generate PDF
        ContractService.generate_contract(
            contract.reservation,
            signature_data=signature_data,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return redirect('contract_detail', pk=contract.pk)
```

### URL Configuration
```python
# apps/contracts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ContractListView.as_view(), name='contract_list'),
    path('<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('<int:pk>/download/', views.ContractDownloadView.as_view(), name='contract_download'),
    path('<int:pk>/print/', views.ContractPrintView.as_view(), name='contract_print'),
    path('<int:pk>/sign/', views.ContractSignView.as_view(), name='contract_sign'),
]
```

### Templates
```html
<!-- templates/contracts/contract_detail.html -->
{% extends "base.html" %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-start mb-6">
            <div>
                <h1 class="text-2xl font-bold">Contract {{ contract.contract_number }}</h1>
                <p class="text-gray-600">Reservation #{{ contract.reservation.confirmation_number }}</p>
            </div>
            <div class="flex space-x-2">
                <a href="{% url 'contract_download' contract.pk %}"
                   class="btn btn-secondary">
                    Download PDF
                </a>
                <a href="{% url 'contract_print' contract.pk %}"
                   class="btn btn-secondary" target="_blank">
                    Print
                </a>
            </div>
        </div>

        <div class="mb-6">
            <span class="px-3 py-1 rounded-full text-sm
                {% if contract.status == 'signed' %}bg-green-100 text-green-800
                {% elif contract.status == 'pending_signature' %}bg-yellow-100 text-yellow-800
                {% else %}bg-gray-100 text-gray-800{% endif %}">
                {{ contract.get_status_display }}
            </span>
        </div>

        <!-- Contract content -->
        <div class="prose max-w-none">
            {{ contract.rental_terms|linebreaks }}
        </div>

        {% if contract.is_signed %}
        <div class="mt-6 p-4 bg-green-50 rounded">
            <h3 class="font-semibold">Signed</h3>
            <p>By: {{ contract.signer_name }}</p>
            <p>Date: {{ contract.signed_at }}</p>
            {% if contract.signature_data %}
            <img src="{{ contract.signature_data }}" alt="Signature" class="mt-2 max-w-xs">
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

## Definition of Done
- [ ] Contract service layer complete
- [ ] Contracts created during checkout
- [ ] Contract detail view works
- [ ] PDF download works
- [ ] Print view available
- [ ] Contract listing with filters
- [ ] Tests written and passing (>95% coverage)
