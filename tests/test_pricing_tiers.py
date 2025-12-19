"""
Tests for FleetFlow Pricing Tiers

Tests the new pricing structure:
- Personal: Free + $2.50/rental
- Starter: $29/mo + $0.75/rental
- Professional: $79/mo, no rental fee
- Business: $199/mo, no rental fee
- Enterprise: Custom, no rental fee
"""
import pytest
from decimal import Decimal

from apps.tenants.models import Tenant, User, TenantUser


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        email='owner@test.com',
        password='testpass123'
    )


class TestPlanChoices:
    """Test that all plan choices are properly defined."""

    def test_personal_plan_exists(self, db):
        """Personal plan should be a valid choice."""
        plan_codes = [code for code, name in Tenant.PLAN_CHOICES]
        assert 'personal' in plan_codes

    def test_all_plans_exist(self, db):
        """All five pricing tiers should exist."""
        plan_codes = [code for code, name in Tenant.PLAN_CHOICES]
        assert 'personal' in plan_codes
        assert 'starter' in plan_codes
        assert 'professional' in plan_codes
        assert 'business' in plan_codes
        assert 'enterprise' in plan_codes

    def test_plan_order(self, db):
        """Plans should be ordered from lowest to highest tier."""
        plan_codes = [code for code, name in Tenant.PLAN_CHOICES]
        assert plan_codes == ['personal', 'starter', 'professional', 'business', 'enterprise']


class TestPlanLimits:
    """Test plan limits configuration."""

    def test_personal_plan_limits(self, db):
        """Personal plan should have correct limits."""
        limits = Tenant.PLAN_LIMITS['personal']
        assert limits['vehicles'] == 3
        assert limits['users'] == 1
        assert limits['base_price'] == 0
        assert limits['rental_fee'] == 2.50

    def test_starter_plan_limits(self, db):
        """Starter plan should have correct limits."""
        limits = Tenant.PLAN_LIMITS['starter']
        assert limits['vehicles'] == 10
        assert limits['users'] == 2
        assert limits['base_price'] == 29
        assert limits['rental_fee'] == 0.75

    def test_professional_plan_limits(self, db):
        """Professional plan should have no rental fee."""
        limits = Tenant.PLAN_LIMITS['professional']
        assert limits['vehicles'] == 25
        assert limits['users'] == 3
        assert limits['base_price'] == 79
        assert limits['rental_fee'] == 0

    def test_business_plan_limits(self, db):
        """Business plan should have no rental fee."""
        limits = Tenant.PLAN_LIMITS['business']
        assert limits['vehicles'] == 100
        assert limits['users'] == 10
        assert limits['base_price'] == 199
        assert limits['rental_fee'] == 0

    def test_enterprise_plan_limits(self, db):
        """Enterprise plan should have unlimited everything."""
        limits = Tenant.PLAN_LIMITS['enterprise']
        assert limits['vehicles'] == 999999
        assert limits['users'] == 999999
        assert limits['rental_fee'] == 0


class TestTenantDefaults:
    """Test that new tenants get correct default values."""

    def test_new_tenant_defaults_to_personal(self, db, owner):
        """New tenants should default to Personal plan."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.plan == 'personal'

    def test_personal_plan_vehicle_limit(self, db, owner):
        """Personal plan should have 3 vehicle limit."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.vehicle_limit == 3

    def test_personal_plan_user_limit(self, db, owner):
        """Personal plan should have 1 user limit."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.user_limit == 1

    def test_personal_plan_rental_fee(self, db, owner):
        """Personal plan should have $2.50 rental fee."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.rental_fee == Decimal('2.50')

    def test_personal_plan_active_by_default(self, db, owner):
        """Personal plan (free) should be active immediately, not trialing."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.subscription_status == 'active'


class TestTenantPlanMethods:
    """Test Tenant model methods for plan management."""

    @pytest.fixture
    def personal_tenant(self, db, owner):
        return Tenant.objects.create(
            name='Personal Tenant',
            slug='personal-tenant',
            owner=owner,
            plan='personal',
            business_name='Personal Business',
            business_email='personal@test.com',
        )

    @pytest.fixture
    def professional_tenant(self, db, owner):
        return Tenant.objects.create(
            name='Pro Tenant',
            slug='pro-tenant',
            owner=owner,
            plan='professional',
            vehicle_limit=25,
            user_limit=3,
            rental_fee=Decimal('0'),
            business_name='Pro Business',
            business_email='pro@test.com',
        )

    def test_has_rental_fee_personal(self, personal_tenant):
        """Personal plan should have rental fee."""
        assert personal_tenant.has_rental_fee() is True

    def test_has_rental_fee_professional(self, professional_tenant):
        """Professional plan should not have rental fee."""
        assert professional_tenant.has_rental_fee() is False

    def test_get_rental_fee(self, personal_tenant):
        """get_rental_fee should return the tenant's rental fee."""
        assert personal_tenant.get_rental_fee() == Decimal('2.50')

    def test_get_base_price_personal(self, personal_tenant):
        """Personal plan base price should be 0."""
        assert personal_tenant.get_base_price() == 0

    def test_get_base_price_professional(self, professional_tenant):
        """Professional plan base price should be 79."""
        assert professional_tenant.get_base_price() == 79

    def test_is_free_plan_personal(self, personal_tenant):
        """Personal plan should be identified as free."""
        assert personal_tenant.is_free_plan() is True

    def test_is_free_plan_professional(self, professional_tenant):
        """Professional plan should not be identified as free."""
        assert professional_tenant.is_free_plan() is False

    def test_get_plan_limits(self, personal_tenant):
        """get_plan_limits should return correct limits."""
        limits = personal_tenant.get_plan_limits()
        assert limits['vehicles'] == 3
        assert limits['users'] == 1
        assert limits['rental_fee'] == 2.50


class TestApplyPlanDefaults:
    """Test the apply_plan_defaults method."""

    def test_apply_starter_defaults(self, db, owner):
        """Applying starter plan should set correct limits."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        tenant.plan = 'starter'
        tenant.apply_plan_defaults()

        assert tenant.vehicle_limit == 10
        assert tenant.user_limit == 2
        assert tenant.rental_fee == Decimal('0.75')

    def test_apply_professional_defaults(self, db, owner):
        """Applying professional plan should remove rental fee."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        tenant.plan = 'professional'
        tenant.apply_plan_defaults()

        assert tenant.vehicle_limit == 25
        assert tenant.user_limit == 3
        assert tenant.rental_fee == Decimal('0')

    def test_apply_business_defaults(self, db, owner):
        """Applying business plan should set high limits."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        tenant.plan = 'business'
        tenant.apply_plan_defaults()

        assert tenant.vehicle_limit == 100
        assert tenant.user_limit == 10
        assert tenant.rental_fee == Decimal('0')


class TestVehicleLimits:
    """Test vehicle limit enforcement."""

    def test_personal_can_add_vehicle_under_limit(self, db, owner):
        """Personal tenant with < 3 vehicles can add more."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.can_add_vehicle() is True

    def test_personal_cannot_add_vehicle_at_limit(self, db, owner):
        """Personal tenant with 3 vehicles cannot add more."""
        from apps.fleet.models import Vehicle

        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )

        # Add 3 vehicles (the limit for personal)
        for i in range(3):
            Vehicle.objects.create(
                tenant=tenant,
                make='Toyota',
                model='Camry',
                year=2023,
                license_plate=f'ABC{i}',
                vin=f'1HGBH41JXMN10918{i}',
                status='available',
                daily_rate=50.00,
            )

        assert tenant.can_add_vehicle() is False


class TestUserLimits:
    """Test user limit enforcement."""

    def test_personal_can_add_user_under_limit(self, db, owner):
        """Personal tenant with no users can add one."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )
        assert tenant.can_add_user() is True

    def test_personal_cannot_add_user_at_limit(self, db, owner):
        """Personal tenant with 1 user cannot add more."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            business_name='Test Business',
            business_email='test@test.com',
        )

        # Add 1 user (the limit for personal)
        TenantUser.objects.create(
            tenant=tenant,
            user=owner,
            role='owner',
            is_active=True
        )

        assert tenant.can_add_user() is False

    def test_starter_can_add_second_user(self, db, owner):
        """Starter tenant with 1 user can add another."""
        tenant = Tenant.objects.create(
            name='Test Tenant',
            slug='test-tenant',
            owner=owner,
            plan='starter',
            vehicle_limit=10,
            user_limit=2,
            rental_fee=Decimal('0.75'),
            business_name='Test Business',
            business_email='test@test.com',
        )

        TenantUser.objects.create(
            tenant=tenant,
            user=owner,
            role='owner',
            is_active=True
        )

        # Starter allows 2 users
        assert tenant.can_add_user() is True
