"""
Platform Admin Views

Views for the FleetFlow super admin dashboard.
All views require superuser access.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from apps.tenants.models import Tenant, TenantUser, User
from .models import PlatformSettings, ImpersonationLog, PlatformAuditLog, log_platform_action
from .decorators import SuperuserRequiredMixin


class PlatformDashboardView(SuperuserRequiredMixin, View):
    """
    Platform admin dashboard with key metrics.

    Shows: total tenants, active/trialing/past_due counts,
    platform revenue, recent signups, trials ending soon.
    """
    template_name = 'platform_admin/dashboard.html'

    def get(self, request):
        # Tenant counts by status
        tenant_stats = Tenant.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(subscription_status='active', is_active=True)),
            trialing=Count('id', filter=Q(subscription_status='trialing', is_active=True)),
            past_due=Count('id', filter=Q(subscription_status='past_due')),
            suspended=Count('id', filter=Q(is_active=False)),
        )

        # Tenant counts by plan
        plan_distribution = Tenant.objects.filter(is_active=True).values('plan').annotate(
            count=Count('id')
        ).order_by('plan')

        # Recent signups (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_signups = Tenant.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]

        # Trials ending soon (within 7 days)
        seven_days = timezone.now() + timedelta(days=7)
        trials_ending = Tenant.objects.filter(
            subscription_status='trialing',
            trial_ends_at__lte=seven_days,
            trial_ends_at__gte=timezone.now(),
            is_active=True
        ).order_by('trial_ends_at')[:10]

        # User counts
        user_stats = User.objects.aggregate(
            total=Count('id'),
            staff=Count('id', filter=Q(is_customer=False)),
            customers=Count('id', filter=Q(is_customer=True)),
            verified=Count('id', filter=Q(email_verified=True)),
        )

        # Recent platform activity
        recent_activity = PlatformAuditLog.objects.select_related(
            'admin_user', 'tenant', 'target_user'
        )[:10]

        # Active impersonation sessions
        active_impersonations = ImpersonationLog.objects.filter(
            ended_at__isnull=True
        ).select_related('admin_user', 'target_user', 'tenant')

        context = {
            'tenant_stats': tenant_stats,
            'plan_distribution': plan_distribution,
            'recent_signups': recent_signups,
            'trials_ending': trials_ending,
            'user_stats': user_stats,
            'recent_activity': recent_activity,
            'active_impersonations': active_impersonations,
        }

        return render(request, self.template_name, context)


class TenantListView(SuperuserRequiredMixin, ListView):
    """
    List all tenants with search and filters.
    """
    model = Tenant
    template_name = 'platform_admin/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 20

    def get_queryset(self):
        queryset = Tenant.objects.select_related('owner').annotate(
            user_count=Count('users'),
        ).order_by('-created_at')

        # Search
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(business_name__icontains=search) |
                Q(owner__email__icontains=search)
            )

        # Filter by plan
        plan = self.request.GET.get('plan', '')
        if plan:
            queryset = queryset.filter(plan=plan)

        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(subscription_status='active', is_active=True)
        elif status == 'trialing':
            queryset = queryset.filter(subscription_status='trialing', is_active=True)
        elif status == 'past_due':
            queryset = queryset.filter(subscription_status='past_due')
        elif status == 'suspended':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['plan_filter'] = self.request.GET.get('plan', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['plan_choices'] = Tenant.PLAN_CHOICES
        return context


class TenantDetailView(SuperuserRequiredMixin, DetailView):
    """
    Detailed view of a single tenant.

    Shows usage stats, users, activity log, subscription details.
    """
    model = Tenant
    template_name = 'platform_admin/tenant_detail.html'
    context_object_name = 'tenant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.object

        # Get tenant users
        tenant_users = TenantUser.objects.filter(
            tenant=tenant
        ).select_related('user').order_by('-role', 'user__email')

        # Get activity logs for this tenant
        activity_logs = PlatformAuditLog.objects.filter(
            tenant=tenant
        ).select_related('admin_user')[:20]

        # Usage statistics
        from apps.fleet.models import Vehicle
        from apps.customers.models import Customer
        from apps.reservations.models import Reservation

        context['tenant_users'] = tenant_users
        context['activity_logs'] = activity_logs
        context['vehicle_count'] = Vehicle.objects.filter(tenant=tenant).count()
        context['customer_count'] = Customer.objects.filter(tenant=tenant).count()
        context['reservation_count'] = Reservation.objects.filter(tenant=tenant).count()
        context['plan_choices'] = Tenant.PLAN_CHOICES
        context['status_choices'] = Tenant.SUBSCRIPTION_STATUS_CHOICES

        return context


class TenantEditView(SuperuserRequiredMixin, View):
    """
    Edit tenant settings (plan, limits, features, status).
    """
    template_name = 'platform_admin/tenant_edit.html'

    def get(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        context = {
            'tenant': tenant,
            'plan_choices': Tenant.PLAN_CHOICES,
            'status_choices': Tenant.SUBSCRIPTION_STATUS_CHOICES,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        old_values = {
            'plan': tenant.plan,
            'subscription_status': tenant.subscription_status,
            'vehicle_limit': tenant.vehicle_limit,
            'user_limit': tenant.user_limit,
            'is_active': tenant.is_active,
        }

        # Update fields
        tenant.plan = request.POST.get('plan', tenant.plan)
        tenant.subscription_status = request.POST.get('subscription_status', tenant.subscription_status)
        tenant.vehicle_limit = int(request.POST.get('vehicle_limit', tenant.vehicle_limit))
        tenant.user_limit = int(request.POST.get('user_limit', tenant.user_limit))
        tenant.save()

        new_values = {
            'plan': tenant.plan,
            'subscription_status': tenant.subscription_status,
            'vehicle_limit': tenant.vehicle_limit,
            'user_limit': tenant.user_limit,
            'is_active': tenant.is_active,
        }

        # Log the change
        log_platform_action(
            admin_user=request.user,
            action='tenant_update',
            tenant=tenant,
            description=f'Updated tenant settings for {tenant.name}',
            changes={'before': old_values, 'after': new_values},
            request=request,
        )

        messages.success(request, f'Tenant "{tenant.name}" updated successfully.')
        return redirect('platform_admin:tenant_detail', pk=tenant.pk)


class TenantSuspendView(SuperuserRequiredMixin, View):
    """
    Suspend or reactivate a tenant.
    """
    def post(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        action = request.POST.get('action', '')

        if action == 'suspend':
            tenant.is_active = False
            tenant.save()
            log_platform_action(
                admin_user=request.user,
                action='tenant_suspend',
                tenant=tenant,
                description=f'Suspended tenant {tenant.name}',
                request=request,
            )
            messages.success(request, f'Tenant "{tenant.name}" has been suspended.')

        elif action == 'reactivate':
            tenant.is_active = True
            tenant.save()
            log_platform_action(
                admin_user=request.user,
                action='tenant_reactivate',
                tenant=tenant,
                description=f'Reactivated tenant {tenant.name}',
                request=request,
            )
            messages.success(request, f'Tenant "{tenant.name}" has been reactivated.')

        return redirect('platform_admin:tenant_detail', pk=tenant.pk)


class PlatformSettingsView(SuperuserRequiredMixin, View):
    """
    Platform-wide settings management.
    """
    template_name = 'platform_admin/settings.html'

    def get(self, request):
        settings_obj = PlatformSettings.get_settings()
        context = {'settings': settings_obj}
        return render(request, self.template_name, context)

    def post(self, request):
        settings_obj = PlatformSettings.get_settings()

        old_values = {
            'require_email_verification': settings_obj.require_email_verification,
            'allow_custom_domains': settings_obj.allow_custom_domains,
            'allow_customer_registration': settings_obj.allow_customer_registration,
            'maintenance_mode': settings_obj.maintenance_mode,
        }

        # Update boolean fields (checkboxes)
        settings_obj.require_email_verification = 'require_email_verification' in request.POST
        settings_obj.allow_custom_domains = 'allow_custom_domains' in request.POST
        settings_obj.allow_customer_registration = 'allow_customer_registration' in request.POST
        settings_obj.maintenance_mode = 'maintenance_mode' in request.POST

        # Update text fields
        settings_obj.platform_name = request.POST.get('platform_name', settings_obj.platform_name)
        settings_obj.maintenance_message = request.POST.get('maintenance_message', settings_obj.maintenance_message)

        settings_obj.save()

        new_values = {
            'require_email_verification': settings_obj.require_email_verification,
            'allow_custom_domains': settings_obj.allow_custom_domains,
            'allow_customer_registration': settings_obj.allow_customer_registration,
            'maintenance_mode': settings_obj.maintenance_mode,
        }

        # Log the change
        log_platform_action(
            admin_user=request.user,
            action='settings_update',
            description='Updated platform settings',
            changes={'before': old_values, 'after': new_values},
            request=request,
        )

        messages.success(request, 'Platform settings updated successfully.')
        return redirect('platform_admin:settings')


class AuditLogListView(SuperuserRequiredMixin, ListView):
    """
    View all platform audit logs.
    """
    model = PlatformAuditLog
    template_name = 'platform_admin/audit_logs.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = PlatformAuditLog.objects.select_related(
            'admin_user', 'tenant', 'target_user'
        ).order_by('-timestamp')

        # Filter by action type
        action = self.request.GET.get('action', '')
        if action:
            queryset = queryset.filter(action=action)

        # Filter by admin
        admin_id = self.request.GET.get('admin', '')
        if admin_id:
            queryset = queryset.filter(admin_user_id=admin_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_choices'] = PlatformAuditLog.ACTION_CHOICES
        context['action_filter'] = self.request.GET.get('action', '')
        return context


class ImpersonateStartView(SuperuserRequiredMixin, View):
    """
    Start impersonating a user.
    """
    template_name = 'platform_admin/impersonate_start.html'

    def get(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)

        # Cannot impersonate yourself
        if target_user.pk == request.user.pk:
            messages.error(request, "You cannot impersonate yourself.")
            return redirect('platform_admin:dashboard')

        # Cannot impersonate other superusers
        if target_user.is_superuser:
            messages.error(request, "You cannot impersonate other superusers.")
            return redirect('platform_admin:dashboard')

        # Get the user's tenant memberships
        tenant_memberships = TenantUser.objects.filter(
            user=target_user, is_active=True
        ).select_related('tenant')

        context = {
            'target_user': target_user,
            'tenant_memberships': tenant_memberships,
        }
        return render(request, self.template_name, context)

    def post(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)

        # Security checks
        if target_user.pk == request.user.pk:
            messages.error(request, "You cannot impersonate yourself.")
            return redirect('platform_admin:dashboard')

        if target_user.is_superuser:
            messages.error(request, "You cannot impersonate other superusers.")
            return redirect('platform_admin:dashboard')

        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason for impersonation.")
            return redirect('platform_admin:impersonate_start', user_id=user_id)

        # Start impersonation
        from .middleware import ImpersonationMiddleware
        log = ImpersonationMiddleware.start_impersonation(request, target_user, reason)

        # Log the action
        log_platform_action(
            admin_user=request.user,
            action='impersonate_start',
            target_user=target_user,
            description=f'Started impersonating {target_user.email}. Reason: {reason}',
            request=request,
        )

        messages.success(request, f'You are now impersonating {target_user.email}.')
        return redirect('dashboard-home')


class ImpersonateEndView(View):
    """
    End the current impersonation session.
    """
    def get(self, request):
        return self.post(request)

    def post(self, request):
        # Must be impersonating to end impersonation
        if not getattr(request, 'is_impersonating', False):
            messages.warning(request, "You are not impersonating anyone.")
            return redirect('dashboard-home')

        impersonator = request.impersonator
        target_user = request.user

        # End impersonation
        from .middleware import ImpersonationMiddleware
        ImpersonationMiddleware.end_impersonation(request)

        # Log the action
        log_platform_action(
            admin_user=impersonator,
            action='impersonate_end',
            target_user=target_user,
            description=f'Ended impersonation of {target_user.email}',
            request=request,
        )

        messages.success(request, f'Impersonation of {target_user.email} has ended.')
        return redirect('platform_admin:dashboard')
