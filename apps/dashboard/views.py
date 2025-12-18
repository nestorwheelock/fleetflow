from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.fleet.models import Vehicle
from apps.customers.models import Customer
from apps.reservations.models import Reservation
from apps.contracts.models import Contract
from apps.tenants.utils import get_tenant_from_request


class TenantMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return qs.filter(tenant=self.request.tenant)
        return qs.none()


@login_required
def dashboard_home(request):
    if not hasattr(request, 'tenant') or not request.tenant:
        return redirect('/no-tenant/')

    tenant = request.tenant
    today = date.today()

    stats = {
        'total_vehicles': Vehicle.objects.filter(tenant=tenant).count(),
        'available_vehicles': Vehicle.objects.filter(tenant=tenant, status='available').count(),
        'rented_vehicles': Vehicle.objects.filter(tenant=tenant, status='rented').count(),
        'total_customers': Customer.objects.filter(tenant=tenant).count(),
        'active_reservations': Reservation.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'checked_out']
        ).count(),
    }

    today_checkouts = Reservation.objects.filter(
        tenant=tenant,
        start_date=today,
        status__in=['pending', 'confirmed']
    ).select_related('vehicle', 'customer')[:5]

    today_checkins = Reservation.objects.filter(
        tenant=tenant,
        end_date=today,
        status='checked_out'
    ).select_related('vehicle', 'customer')[:5]

    upcoming_reservations = Reservation.objects.filter(
        tenant=tenant,
        start_date__gte=today,
        status__in=['pending', 'confirmed']
    ).select_related('vehicle', 'customer').order_by('start_date')[:10]

    month_start = today.replace(day=1)
    revenue_this_month = Reservation.objects.filter(
        tenant=tenant,
        status__in=['completed', 'checked_out'],
        start_date__gte=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    context = {
        'stats': stats,
        'today_checkouts': today_checkouts,
        'today_checkins': today_checkins,
        'upcoming_reservations': upcoming_reservations,
        'revenue_this_month': revenue_this_month,
        'today': today,
    }

    return render(request, 'dashboard/home.html', context)


class VehicleListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Vehicle
    template_name = 'dashboard/vehicles/list.html'
    context_object_name = 'vehicles'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(make__icontains=search) |
                Q(model__icontains=search) |
                Q(license_plate__icontains=search)
            )
        return qs


class VehicleDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Vehicle
    template_name = 'dashboard/vehicles/detail.html'
    context_object_name = 'vehicle'


class VehicleCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Vehicle
    template_name = 'dashboard/vehicles/form.html'
    fields = ['category', 'make', 'model', 'year', 'license_plate', 'vin',
              'color', 'daily_rate', 'transmission', 'fuel_type', 'seats']

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        return super().form_valid(form)

    def get_success_url(self):
        return '/dashboard/vehicles/'


class VehicleUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Vehicle
    template_name = 'dashboard/vehicles/form.html'
    fields = ['category', 'make', 'model', 'year', 'license_plate', 'vin',
              'color', 'status', 'daily_rate', 'transmission', 'fuel_type', 'seats']

    def get_success_url(self):
        return f'/dashboard/vehicles/{self.object.pk}/'


class VehicleDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = Vehicle
    template_name = 'dashboard/vehicles/delete.html'
    success_url = reverse_lazy('vehicle-list')

    def get_success_url(self):
        messages.success(self.request, 'Vehicle deleted successfully.')
        return '/dashboard/vehicles/'


class CustomerListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Customer
    template_name = 'dashboard/customers/list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        return qs


class CustomerDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Customer
    template_name = 'dashboard/customers/detail.html'
    context_object_name = 'customer'


class CustomerCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Customer
    template_name = 'dashboard/customers/form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code',
              'license_number', 'license_state', 'license_expiry', 'license_image_front', 'license_image_back']

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Customer created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return '/dashboard/customers/'


class CustomerUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Customer
    template_name = 'dashboard/customers/form.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code',
              'license_number', 'license_state', 'license_expiry', 'license_image_front', 'license_image_back']

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/dashboard/customers/{self.object.pk}/'


class CustomerDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = Customer
    template_name = 'dashboard/customers/delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Customer deleted successfully.')
        return '/dashboard/customers/'


class ReservationListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Reservation
    template_name = 'dashboard/reservations/list.html'
    context_object_name = 'reservations'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('vehicle', 'customer')
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class ReservationDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Reservation
    template_name = 'dashboard/reservations/detail.html'
    context_object_name = 'reservation'


class ReservationCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Reservation
    template_name = 'dashboard/reservations/form.html'
    fields = ['vehicle', 'customer', 'start_date', 'end_date', 'daily_rate']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tenant = self.request.tenant
        form.fields['vehicle'].queryset = Vehicle.objects.filter(tenant=tenant, status='available')
        form.fields['customer'].queryset = Customer.objects.filter(tenant=tenant)
        return form

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Reservation created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return '/dashboard/reservations/'


class ReservationUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Reservation
    template_name = 'dashboard/reservations/form.html'
    fields = ['vehicle', 'customer', 'start_date', 'end_date', 'daily_rate']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tenant = self.request.tenant
        form.fields['vehicle'].queryset = Vehicle.objects.filter(tenant=tenant)
        form.fields['customer'].queryset = Customer.objects.filter(tenant=tenant)
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Reservation updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/dashboard/reservations/{self.object.pk}/'


@login_required
def reservation_cancel(request, pk):
    if not hasattr(request, 'tenant') or not request.tenant:
        return redirect('/no-tenant/')

    reservation = get_object_or_404(Reservation, pk=pk, tenant=request.tenant)

    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Reservation cancelled successfully.')
        return redirect('/dashboard/reservations/')

    return render(request, 'dashboard/reservations/cancel.html', {'reservation': reservation})


@login_required
def reservation_calendar(request):
    if not hasattr(request, 'tenant') or not request.tenant:
        return redirect('/no-tenant/')
    return render(request, 'dashboard/reservations/calendar.html')


@login_required
def reservation_checkout(request, pk):
    if not hasattr(request, 'tenant') or not request.tenant:
        return redirect('/no-tenant/')

    reservation = get_object_or_404(
        Reservation, pk=pk, tenant=request.tenant
    )

    if request.method == 'POST':
        mileage = request.POST.get('mileage')
        try:
            reservation.checkout(mileage=int(mileage) if mileage else None)
            return redirect(f'/dashboard/reservations/{pk}/')
        except Exception as e:
            context = {'reservation': reservation, 'error': str(e)}
            return render(request, 'dashboard/reservations/checkout.html', context)

    return render(request, 'dashboard/reservations/checkout.html', {'reservation': reservation})


@login_required
def reservation_checkin(request, pk):
    if not hasattr(request, 'tenant') or not request.tenant:
        return redirect('/no-tenant/')

    reservation = get_object_or_404(
        Reservation, pk=pk, tenant=request.tenant
    )

    if request.method == 'POST':
        mileage = request.POST.get('mileage')
        try:
            reservation.checkin(mileage=int(mileage) if mileage else None)
            return redirect(f'/dashboard/reservations/{pk}/')
        except Exception as e:
            context = {'reservation': reservation, 'error': str(e)}
            return render(request, 'dashboard/reservations/checkin.html', context)

    return render(request, 'dashboard/reservations/checkin.html', {'reservation': reservation})


class ContractListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Contract
    template_name = 'dashboard/contracts/list.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('reservation', 'reservation__customer')


class ContractDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Contract
    template_name = 'dashboard/contracts/detail.html'
    context_object_name = 'contract'


@login_required
def contract_pdf(request, pk):
    if not hasattr(request, 'tenant') or not request.tenant:
        return redirect('/no-tenant/')

    contract = get_object_or_404(Contract, pk=pk, tenant=request.tenant)
    pdf_content = contract.generate_pdf()

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{contract.contract_number}.pdf"'
    return response


class DashboardStatsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)
        today = date.today()

        data = {
            'total_vehicles': Vehicle.objects.filter(tenant=tenant).count(),
            'total_customers': Customer.objects.filter(tenant=tenant).count(),
            'active_reservations': Reservation.objects.filter(
                tenant=tenant,
                status__in=['confirmed', 'checked_out']
            ).count(),
        }

        return Response(data)


class DashboardTodayAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)
        today = date.today()

        from apps.reservations.serializers import ReservationListSerializer

        checkouts = Reservation.objects.filter(
            tenant=tenant,
            start_date=today,
            status__in=['pending', 'confirmed']
        ).select_related('vehicle', 'customer')

        checkins = Reservation.objects.filter(
            tenant=tenant,
            end_date=today,
            status='checked_out'
        ).select_related('vehicle', 'customer')

        return Response({
            'checkouts': ReservationListSerializer(checkouts, many=True).data,
            'checkins': ReservationListSerializer(checkins, many=True).data,
        })


class DashboardRevenueAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)
        today = date.today()

        today_revenue = Reservation.objects.filter(
            tenant=tenant,
            status__in=['completed', 'checked_out'],
            start_date=today
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        week_start = today - timedelta(days=today.weekday())
        week_revenue = Reservation.objects.filter(
            tenant=tenant,
            status__in=['completed', 'checked_out'],
            start_date__gte=week_start
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        month_start = today.replace(day=1)
        month_revenue = Reservation.objects.filter(
            tenant=tenant,
            status__in=['completed', 'checked_out'],
            start_date__gte=month_start
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        return Response({
            'today': str(today_revenue),
            'this_week': str(week_revenue),
            'this_month': str(month_revenue),
        })


class DashboardFleetStatusAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)
        status_counts = Vehicle.objects.filter(tenant=tenant).values('status').annotate(count=Count('id'))

        data = {
            'available': 0,
            'rented': 0,
            'maintenance': 0,
            'unavailable': 0,
        }

        for item in status_counts:
            data[item['status']] = item['count']

        return Response(data)


class DashboardUpcomingAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)
        today = date.today()

        from apps.reservations.serializers import ReservationListSerializer

        upcoming = Reservation.objects.filter(
            tenant=tenant,
            start_date__gte=today,
            status__in=['pending', 'confirmed']
        ).select_related('vehicle', 'customer').order_by('start_date')[:10]

        return Response(ReservationListSerializer(upcoming, many=True).data)


class QuickActionNewReservationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)

        from apps.reservations.serializers import ReservationSerializer
        data = request.data.copy()
        serializer = ReservationSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(tenant=tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuickActionNewCustomerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)

        from apps.customers.serializers import CustomerSerializer
        serializer = CustomerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(tenant=tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuickActionVehicleStatusAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant = get_tenant_from_request(request)
        if not tenant:
            return Response({'error': 'No tenant'}, status=400)

        vehicle_id = request.data.get('vehicle')
        new_status = request.data.get('status')

        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id, tenant=tenant)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=404)

        if new_status not in dict(Vehicle.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=400)

        vehicle.status = new_status
        vehicle.save(update_fields=['status', 'updated_at'])
        return Response({'status': vehicle.status})


@login_required
def customer_combined_license(request, pk):
    """Generate a combined image with license front on top, back on bottom."""
    from PIL import Image
    from io import BytesIO
    from django.http import HttpResponse, Http404

    customer = get_object_or_404(Customer, pk=pk, tenant=request.tenant)

    if not customer.license_image_front or not customer.license_image_back:
        raise Http404("License images not available")

    # Open both images
    front_img = Image.open(customer.license_image_front.path)
    back_img = Image.open(customer.license_image_back.path)

    # Resize both to same width, maintaining aspect ratio
    target_width = max(front_img.width, back_img.width)

    if front_img.width != target_width:
        ratio = target_width / front_img.width
        front_img = front_img.resize((target_width, int(front_img.height * ratio)), Image.Resampling.LANCZOS)

    if back_img.width != target_width:
        ratio = target_width / back_img.width
        back_img = back_img.resize((target_width, int(back_img.height * ratio)), Image.Resampling.LANCZOS)

    # Create combined image (front on top, back on bottom)
    combined_height = front_img.height + back_img.height
    combined_img = Image.new('RGB', (target_width, combined_height), 'white')
    combined_img.paste(front_img, (0, 0))
    combined_img.paste(back_img, (0, front_img.height))

    # Save to buffer
    buffer = BytesIO()
    combined_img.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/jpeg')
