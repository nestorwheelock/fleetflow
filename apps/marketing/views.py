from django.views.generic import TemplateView, FormView, ListView
from django.http import JsonResponse
from django.db.models import Q, Count
from django.urls import reverse_lazy

from apps.tenants.models import Tenant
from .models import LeadCapture, ReferralCredit
from .forms import SignupLeadForm, ReferralForm, RentalSearchForm


class HomePageView(TemplateView):
    """Main marketing landing page."""
    template_name = 'marketing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = SignupLeadForm()
        context['referral_form'] = ReferralForm()
        context['search_form'] = RentalSearchForm()
        context['plan_limits'] = Tenant.PLAN_LIMITS
        context['testimonials'] = self.get_testimonials()
        return context

    def get_testimonials(self):
        return [
            {
                'quote': "FleetFlow transformed my side hustle into a real business. I started with 2 cars, now I manage 15.",
                'author': "Maria G.",
                'location': "Austin, TX",
                'company': "Ron's Rentals",
                'rating': 5,
            },
            {
                'quote': "The scheduling calendar alone saved me hours every week. No more double bookings!",
                'author': "James T.",
                'location': "Dallas, TX",
                'company': "City Cars",
                'rating': 5,
            },
            {
                'quote': "I was skeptical at first, but the free tier let me try it risk-free. Now I'm on Professional.",
                'author': "Sarah K.",
                'location': "Houston, TX",
                'company': "Budget Wheels",
                'rating': 5,
            },
            {
                'quote': "Customer support is amazing. They helped me set up everything in under an hour.",
                'author': "Mike R.",
                'location': "San Antonio, TX",
                'company': "Quick Rentals",
                'rating': 5,
            },
        ]


class LeadCaptureView(FormView):
    """AJAX endpoint for capturing email leads."""
    form_class = SignupLeadForm

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.lead_type = self.request.POST.get('lead_type', 'owner')
        lead.source = self.request.POST.get('source', 'homepage')
        lead.save()
        return JsonResponse({
            'success': True,
            'message': 'Thanks! Check your email to get started.'
        })

    def form_invalid(self, form):
        if 'email' in form.errors:
            if 'unique' in str(form.errors['email']):
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! You\'re already signed up.'
                })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


class ReferralView(FormView):
    """Handle referral submissions."""
    form_class = ReferralForm
    template_name = 'marketing/referral_success.html'
    success_url = reverse_lazy('marketing:home')

    def form_valid(self, form):
        form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Referral sent! They\'ll receive $25 credit when they sign up.'
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)


class RentalSearchView(ListView):
    """Search for rental companies by location."""
    model = Tenant
    template_name = 'marketing/search_results.html'
    context_object_name = 'tenants'
    paginate_by = 12

    def get_queryset(self):
        queryset = Tenant.objects.filter(is_active=True)
        location = self.request.GET.get('location', '').strip()

        if location:
            queryset = queryset.filter(
                Q(business_name__icontains=location) |
                Q(name__icontains=location) |
                Q(slug__icontains=location)
            )

        return queryset.annotate(
            vehicle_count=Count('vehicle')
        ).order_by('-vehicle_count')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = RentalSearchForm(self.request.GET)
        context['location'] = self.request.GET.get('location', '')
        context['pickup_date'] = self.request.GET.get('pickup_date', '')
        context['return_date'] = self.request.GET.get('return_date', '')
        return context


class PricingView(TemplateView):
    """Detailed pricing page."""
    template_name = 'marketing/pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plan_limits'] = Tenant.PLAN_LIMITS
        context['plan_choices'] = Tenant.PLAN_CHOICES
        return context


class FeaturesView(TemplateView):
    """Features overview page."""
    template_name = 'marketing/features.html'
