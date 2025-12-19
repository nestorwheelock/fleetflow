"""
Tests for marketing landing page and related views.
"""
import pytest
from django.test import Client
from django.urls import reverse

from apps.marketing.models import LeadCapture, ReferralCredit
from apps.tenants.models import Tenant, User


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        email='owner@test.com',
        password='testpass123'
    )


@pytest.fixture
def tenant(db, owner):
    return Tenant.objects.create(
        name='Test Tenant',
        slug='test-tenant',
        owner=owner,
        business_name='Austin Car Rentals',
        business_email='test@business.com',
    )


@pytest.mark.django_db
class TestMarketingHomePage:
    """Tests for the marketing homepage."""

    def test_homepage_accessible(self, client):
        """Homepage should return 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_homepage_contains_hero(self, client):
        """Homepage should contain hero section."""
        response = client.get('/')
        content = response.content.decode()
        assert 'The Smart Way to Manage Car Rentals' in content

    def test_homepage_contains_pricing(self, client):
        """Homepage should show pricing information."""
        response = client.get('/')
        content = response.content.decode()
        assert 'Personal' in content
        assert 'Starter' in content
        assert 'Professional' in content

    def test_homepage_contains_signup_form(self, client):
        """Homepage should contain signup form."""
        response = client.get('/')
        content = response.content.decode()
        assert 'Enter your email' in content
        assert 'Start Free Trial' in content

    def test_homepage_contains_search_form(self, client):
        """Homepage should contain rental search form."""
        response = client.get('/')
        content = response.content.decode()
        assert 'City or ZIP code' in content
        assert 'Search Rentals' in content

    def test_homepage_contains_testimonials(self, client):
        """Homepage should show testimonials."""
        response = client.get('/')
        content = response.content.decode()
        assert 'Trusted by Rental Businesses' in content

    def test_homepage_contains_features(self, client):
        """Homepage should highlight features."""
        response = client.get('/')
        content = response.content.decode()
        assert 'Smart Scheduling' in content
        assert 'Digital Contracts' in content

    def test_homepage_contains_referral_section(self, client):
        """Homepage should have referral section."""
        response = client.get('/')
        content = response.content.decode()
        assert 'Know Someone Who Should Be on FleetFlow' in content
        assert '$25 credit' in content


@pytest.mark.django_db
class TestPricingPage:
    """Tests for the pricing page."""

    def test_pricing_page_accessible(self, client):
        """Pricing page should return 200."""
        response = client.get(reverse('marketing:pricing'))
        assert response.status_code == 200

    def test_pricing_shows_all_plans(self, client):
        """Pricing page should show all plan tiers."""
        response = client.get(reverse('marketing:pricing'))
        content = response.content.decode()
        assert 'Personal' in content
        assert 'Starter' in content
        assert 'Professional' in content
        assert 'Business' in content
        assert 'Enterprise' in content

    def test_pricing_shows_faq(self, client):
        """Pricing page should show FAQ section."""
        response = client.get(reverse('marketing:pricing'))
        content = response.content.decode()
        assert 'Frequently Asked Questions' in content


@pytest.mark.django_db
class TestFeaturesPage:
    """Tests for the features page."""

    def test_features_page_accessible(self, client):
        """Features page should return 200."""
        response = client.get(reverse('marketing:features'))
        assert response.status_code == 200

    def test_features_shows_all_features(self, client):
        """Features page should list all features."""
        response = client.get(reverse('marketing:features'))
        content = response.content.decode()
        assert 'Smart Scheduling' in content
        assert 'Digital Contracts' in content
        assert 'Customer Portal' in content
        assert 'Real-Time Analytics' in content


@pytest.mark.django_db
class TestRentalSearch:
    """Tests for rental search functionality."""

    def test_search_page_accessible(self, client):
        """Search page should return 200."""
        response = client.get(reverse('marketing:rental-search'))
        assert response.status_code == 200

    def test_search_with_location(self, client, tenant):
        """Search should filter by location."""
        response = client.get(reverse('marketing:rental-search'), {'location': 'Austin'})
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Austin Car Rentals' in content

    def test_search_no_results(self, client, tenant):
        """Search with no matches should show empty state."""
        response = client.get(reverse('marketing:rental-search'), {'location': 'Nowhere'})
        assert response.status_code == 200
        content = response.content.decode()
        assert 'No rental companies found' in content

    def test_search_shows_tenant_link(self, client, tenant):
        """Search results should link to tenant subdomain."""
        response = client.get(reverse('marketing:rental-search'), {'location': 'Austin'})
        content = response.content.decode()
        assert 'test-tenant' in content


class TestLeadCapture:
    """Tests for lead capture functionality."""

    def test_lead_capture_creates_lead(self, client, db):
        """Lead capture should create LeadCapture record."""
        response = client.post(
            reverse('marketing:lead-capture'),
            {
                'email': 'newlead@test.com',
                'lead_type': 'owner',
                'source': 'homepage'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        assert LeadCapture.objects.filter(email='newlead@test.com').exists()

    def test_lead_capture_duplicate_email(self, client, db):
        """Lead capture should handle duplicate emails by showing error or welcome back."""
        LeadCapture.objects.create(email='existing@test.com', lead_type='owner')

        response = client.post(
            reverse('marketing:lead-capture'),
            {
                'email': 'existing@test.com',
                'lead_type': 'owner',
                'source': 'homepage'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Should return either success (welcome back) or error (duplicate)
        assert response.status_code in [200, 400]

    def test_lead_capture_invalid_email(self, client, db):
        """Lead capture should reject invalid emails."""
        response = client.post(
            reverse('marketing:lead-capture'),
            {
                'email': 'notanemail',
                'lead_type': 'owner',
                'source': 'homepage'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 400


class TestReferralSystem:
    """Tests for referral credit system."""

    def test_referral_creates_credit(self, client, db):
        """Referral form should create ReferralCredit record."""
        response = client.post(
            reverse('marketing:referral'),
            {
                'referrer_email': 'referrer@test.com',
                'referred_email': 'referred@test.com',
                'referral_type': 'owner'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        assert ReferralCredit.objects.filter(
            referrer_email='referrer@test.com',
            referred_email='referred@test.com'
        ).exists()

    def test_referral_default_amount(self, client, db):
        """Referral should have $25 default credit amount."""
        client.post(
            reverse('marketing:referral'),
            {
                'referrer_email': 'referrer@test.com',
                'referred_email': 'referred@test.com',
                'referral_type': 'owner'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        credit = ReferralCredit.objects.get(referrer_email='referrer@test.com')
        assert credit.credit_amount == 25.00

    def test_referral_cannot_self_refer(self, client, db):
        """Users should not be able to refer themselves."""
        response = client.post(
            reverse('marketing:referral'),
            {
                'referrer_email': 'same@test.com',
                'referred_email': 'same@test.com',
                'referral_type': 'owner'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 400


class TestMarketingModels:
    """Tests for marketing models."""

    def test_lead_capture_str(self, db):
        """LeadCapture should have readable string representation."""
        lead = LeadCapture.objects.create(
            email='test@test.com',
            lead_type='owner'
        )
        assert 'test@test.com' in str(lead)

    def test_referral_credit_str(self, db):
        """ReferralCredit should have readable string representation."""
        credit = ReferralCredit.objects.create(
            referrer_email='a@test.com',
            referred_email='b@test.com',
            referral_type='owner'
        )
        assert 'a@test.com' in str(credit)
        assert 'b@test.com' in str(credit)

    def test_lead_capture_ordering(self, db):
        """Leads should be ordered by creation date (newest first)."""
        lead1 = LeadCapture.objects.create(email='first@test.com', lead_type='owner')
        lead2 = LeadCapture.objects.create(email='second@test.com', lead_type='owner')

        leads = list(LeadCapture.objects.all())
        assert leads[0] == lead2
        assert leads[1] == lead1


@pytest.mark.django_db
class TestMarketingURLs:
    """Tests for marketing URL patterns."""

    def test_home_url(self, client):
        """Root URL should resolve to marketing home."""
        response = client.get('/')
        assert response.status_code == 200

    def test_pricing_url(self, client):
        """Pricing URL should be accessible."""
        response = client.get('/pricing/')
        assert response.status_code == 200

    def test_features_url(self, client):
        """Features URL should be accessible."""
        response = client.get('/features/')
        assert response.status_code == 200

    def test_search_url(self, client):
        """Search URL should be accessible."""
        response = client.get('/search/')
        assert response.status_code == 200
