"""
Public Views

Public-facing views for tenant landing pages, vehicle gallery, and contact info.
These views are accessible to customers visiting a tenant's subdomain.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from apps.fleet.models import Vehicle
from apps.tenants.models import Tenant, TenantBranding, User
from apps.customers.models import Customer, CustomerDocument
from apps.reservations.models import Reservation


class TenantRequiredMixin:
    """Mixin that requires a tenant in request context."""

    def dispatch(self, request, *args, **kwargs):
        if not getattr(request, 'tenant', None):
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)


class LandingPageView(TenantRequiredMixin, View):
    """
    Public landing page for a tenant.

    Shows tenant branding, available vehicles, and contact info.
    """
    template_name = 'public/landing.html'

    def get(self, request):
        tenant = request.tenant

        try:
            branding = tenant.branding
        except TenantBranding.DoesNotExist:
            branding = None

        featured_vehicles = Vehicle.objects.filter(
            tenant=tenant,
            status='available'
        ).prefetch_related('photos')[:6]

        context = {
            'tenant': tenant,
            'branding': branding,
            'featured_vehicles': featured_vehicles,
        }

        return render(request, self.template_name, context)


class VehicleGalleryView(TenantRequiredMixin, ListView):
    """
    Public vehicle gallery for a tenant.

    Shows all available vehicles with filtering options.
    """
    model = Vehicle
    template_name = 'public/vehicles.html'
    context_object_name = 'vehicles'
    paginate_by = 12

    def get_queryset(self):
        tenant = self.request.tenant
        queryset = Vehicle.objects.filter(
            tenant=tenant,
            status='available'
        ).prefetch_related('photos')

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(daily_rate__gte=min_price)

        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(daily_rate__lte=max_price)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(make__icontains=search) |
                Q(model__icontains=search)
            )

        sort = self.request.GET.get('sort', 'daily_rate')
        if sort == 'price_high':
            queryset = queryset.order_by('-daily_rate')
        elif sort == 'newest':
            queryset = queryset.order_by('-year')
        else:
            queryset = queryset.order_by('daily_rate')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant

        try:
            context['branding'] = tenant.branding
        except TenantBranding.DoesNotExist:
            context['branding'] = None

        context['categories'] = Vehicle.CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort', 'daily_rate')
        context['search'] = self.request.GET.get('search', '')

        return context


class VehicleDetailView(TenantRequiredMixin, DetailView):
    """
    Public vehicle detail page.

    Shows full vehicle details, photos, and booking button.
    """
    model = Vehicle
    template_name = 'public/vehicle_detail.html'
    context_object_name = 'vehicle'

    def get_queryset(self):
        return Vehicle.objects.filter(
            tenant=self.request.tenant
        ).prefetch_related('photos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant

        try:
            context['branding'] = tenant.branding
        except TenantBranding.DoesNotExist:
            context['branding'] = None

        return context


class ContactView(TenantRequiredMixin, View):
    """
    Contact page for tenant.

    Shows business contact information and location.
    """
    template_name = 'public/contact.html'

    def get(self, request):
        tenant = request.tenant

        try:
            branding = tenant.branding
        except TenantBranding.DoesNotExist:
            branding = None

        context = {
            'tenant': tenant,
            'branding': branding,
        }

        return render(request, self.template_name, context)


class CustomerRegisterView(TenantRequiredMixin, View):
    """
    Customer registration for a tenant.
    """
    template_name = 'public/customer/register.html'

    def get_branding(self, tenant):
        try:
            return tenant.branding
        except TenantBranding.DoesNotExist:
            return None

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('public:customer_portal')

        tenant = request.tenant
        context = {
            'tenant': tenant,
            'branding': self.get_branding(tenant),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        tenant = request.tenant
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')

        errors = []

        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if password != password_confirm:
            errors.append('Passwords do not match')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')

        if User.objects.filter(email__iexact=email).exists():
            errors.append('An account with this email already exists')

        if errors:
            context = {
                'tenant': tenant,
                'branding': self.get_branding(tenant),
                'errors': errors,
                'form_data': {
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                }
            }
            return render(request, self.template_name, context)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_customer=True,
            phone=phone,
        )

        Customer.objects.create(
            tenant=tenant,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        login(request, user, backend='apps.tenants.backends.EmailBackend')
        messages.success(request, 'Your account has been created successfully!')
        return redirect('public:customer_portal')


class CustomerPortalView(TenantRequiredMixin, LoginRequiredMixin, View):
    """
    Customer portal dashboard.
    """
    template_name = 'public/customer/portal.html'
    login_url = '/login/'

    def get(self, request):
        tenant = request.tenant
        user = request.user

        try:
            customer = Customer.objects.get(tenant=tenant, email=user.email)
        except Customer.DoesNotExist:
            customer = None

        reservations = []
        documents = []
        if customer:
            reservations = Reservation.objects.filter(
                tenant=tenant,
                customer=customer
            ).order_by('-created_at')[:5]
            documents = CustomerDocument.objects.filter(
                tenant=tenant,
                customer=customer
            ).order_by('-uploaded_at')

        try:
            branding = tenant.branding
        except TenantBranding.DoesNotExist:
            branding = None

        context = {
            'tenant': tenant,
            'branding': branding,
            'customer': customer,
            'reservations': reservations,
            'documents': documents,
        }
        return render(request, self.template_name, context)


class CustomerDocumentUploadView(TenantRequiredMixin, LoginRequiredMixin, View):
    """
    Document upload for customers.
    """
    template_name = 'public/customer/documents.html'
    login_url = '/login/'

    def get(self, request):
        tenant = request.tenant
        user = request.user

        try:
            customer = Customer.objects.get(tenant=tenant, email=user.email)
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('public:customer_portal')

        documents = CustomerDocument.objects.filter(
            tenant=tenant,
            customer=customer
        ).order_by('-uploaded_at')

        try:
            branding = tenant.branding
        except TenantBranding.DoesNotExist:
            branding = None

        context = {
            'tenant': tenant,
            'branding': branding,
            'customer': customer,
            'documents': documents,
            'document_types': CustomerDocument.DOCUMENT_TYPES,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        tenant = request.tenant
        user = request.user

        try:
            customer = Customer.objects.get(tenant=tenant, email=user.email)
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('public:customer_portal')

        document_type = request.POST.get('document_type')
        document_file = request.FILES.get('document')
        description = request.POST.get('description', '')

        if not document_file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('public:customer_documents')

        CustomerDocument.objects.create(
            tenant=tenant,
            customer=customer,
            document_type=document_type,
            file=document_file,
            description=description,
            verification_status='pending',
        )

        messages.success(request, 'Document uploaded successfully. It will be reviewed by staff.')
        return redirect('public:customer_documents')


class CustomerReservationsView(TenantRequiredMixin, LoginRequiredMixin, View):
    """
    Customer reservations list.
    """
    template_name = 'public/customer/reservations.html'
    login_url = '/login/'

    def get(self, request):
        tenant = request.tenant
        user = request.user

        try:
            customer = Customer.objects.get(tenant=tenant, email=user.email)
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('public:customer_portal')

        reservations = Reservation.objects.filter(
            tenant=tenant,
            customer=customer
        ).select_related('vehicle').order_by('-start_date')

        try:
            branding = tenant.branding
        except TenantBranding.DoesNotExist:
            branding = None

        context = {
            'tenant': tenant,
            'branding': branding,
            'customer': customer,
            'reservations': reservations,
        }
        return render(request, self.template_name, context)
