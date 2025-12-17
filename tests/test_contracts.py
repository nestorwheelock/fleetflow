import pytest
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal


class TestContractModel:
    def test_contract_creation(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            contract_number='CTR-2025-0001',
            status='draft',
        )
        assert contract.pk is not None
        assert contract.contract_number == 'CTR-2025-0001'

    def test_contract_str_representation(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            contract_number='CTR-2025-0002',
            status='draft',
        )
        assert str(contract) == 'CTR-2025-0002'

    def test_contract_number_unique_per_tenant(self, db, tenant, reservation, vehicle, customer):
        from apps.contracts.models import Contract
        from apps.reservations.models import Reservation
        Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            contract_number='UNIQUE-001',
            status='draft',
        )
        res2 = Reservation.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            customer=customer,
            start_date=date.today() + timedelta(days=100),
            end_date=date.today() + timedelta(days=103),
            daily_rate=Decimal('50.00'),
        )
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Contract.objects.create(
                tenant=tenant,
                reservation=res2,
                contract_number='UNIQUE-001',
                status='draft',
            )

    def test_contract_auto_number_generation(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            status='draft',
        )
        assert contract.contract_number is not None
        assert contract.contract_number.startswith('CTR-')

    def test_contract_status_choices(self, db, tenant, vehicle, customer):
        from apps.contracts.models import Contract
        from apps.reservations.models import Reservation
        from decimal import Decimal
        valid_statuses = ['draft', 'pending_signature', 'signed', 'active', 'completed', 'cancelled']
        for i, status in enumerate(valid_statuses):
            res = Reservation.objects.create(
                tenant=tenant,
                vehicle=vehicle,
                customer=customer,
                start_date=date.today() + timedelta(days=200 + i * 10),
                end_date=date.today() + timedelta(days=203 + i * 10),
                daily_rate=Decimal('50.00'),
            )
            contract = Contract.objects.create(
                tenant=tenant,
                reservation=res,
                contract_number=f'STATUS-{status.upper()}',
                status=status,
            )
            assert contract.status == status

    def test_contract_customer_signature(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        from django.utils import timezone
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            status='pending_signature',
        )
        contract.customer_signature = 'data:image/png;base64,iVBORw0KGgo...'
        contract.customer_signed_at = timezone.now()
        contract.status = 'signed'
        contract.save()
        contract.refresh_from_db()
        assert contract.status == 'signed'
        assert contract.customer_signed_at is not None

    def test_contract_terms_and_conditions(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        terms = 'Standard rental terms and conditions...'
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            terms_and_conditions=terms,
        )
        assert contract.terms_and_conditions == terms

    def test_contract_pdf_generated(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            status='signed',
        )
        pdf_data = contract.generate_pdf()
        assert pdf_data is not None
        assert len(pdf_data) > 0

    def test_contract_tenant_isolation(self, db, tenant, reservation, user):
        from apps.tenants.models import Tenant
        from apps.contracts.models import Contract
        Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            contract_number='TENANT-ISO-001',
        )
        other_tenant = Tenant.objects.create(
            name='Other Contract Rental',
            slug='other-contract-rental',
            owner=user,
            plan='starter',
            business_name='Other Co',
            business_email='other@test.com',
            vehicle_limit=10,
            user_limit=1,
        )
        tenant_contracts = Contract.objects.filter(tenant=tenant)
        other_tenant_contracts = Contract.objects.filter(tenant=other_tenant)
        assert tenant_contracts.count() == 1
        assert other_tenant_contracts.count() == 0


class TestConditionReportModel:
    def test_checkout_condition_report(self, db, tenant, reservation):
        from apps.contracts.models import Contract, ConditionReport
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        report = ConditionReport.objects.create(
            contract=contract,
            report_type='checkout',
            fuel_level='full',
            mileage=15000,
            exterior_condition='good',
            interior_condition='good',
            notes='Vehicle in good condition',
        )
        assert report.pk is not None
        assert report.report_type == 'checkout'

    def test_checkin_condition_report(self, db, tenant, reservation):
        from apps.contracts.models import Contract, ConditionReport
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        checkout_report = ConditionReport.objects.create(
            contract=contract,
            report_type='checkout',
            fuel_level='full',
            mileage=15000,
            exterior_condition='good',
            interior_condition='good',
        )
        checkin_report = ConditionReport.objects.create(
            contract=contract,
            report_type='checkin',
            fuel_level='3/4',
            mileage=15250,
            exterior_condition='good',
            interior_condition='good',
        )
        assert checkin_report.pk is not None
        assert checkin_report.mileage == 15250

    def test_condition_report_damages(self, db, tenant, reservation):
        from apps.contracts.models import Contract, ConditionReport
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        report = ConditionReport.objects.create(
            contract=contract,
            report_type='checkin',
            fuel_level='full',
            mileage=15500,
            exterior_condition='damaged',
            interior_condition='good',
            damages=[
                {'location': 'front_bumper', 'description': 'Scratch 10cm', 'severity': 'minor'},
            ],
        )
        assert len(report.damages) == 1
        assert report.damages[0]['location'] == 'front_bumper'

    def test_condition_report_photos(self, db, tenant, reservation):
        from apps.contracts.models import Contract, ConditionReport, ConditionReportPhoto
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        report = ConditionReport.objects.create(
            contract=contract,
            report_type='checkout',
            fuel_level='full',
            mileage=15000,
            exterior_condition='good',
            interior_condition='good',
        )
        photo = ConditionReportPhoto.objects.create(
            condition_report=report,
            location='front',
            description='Front view',
        )
        assert photo.pk is not None


class TestContractAPI:
    def test_contract_list_requires_auth(self, api_client):
        response = api_client.get('/api/contracts/')
        assert response.status_code == 403

    def test_contract_list(self, tenant_client, reservation):
        from apps.contracts.models import Contract
        client, tenant = tenant_client
        Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        response = client.get('/api/contracts/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_contract_create(self, tenant_client, reservation):
        client, tenant = tenant_client
        data = {
            'reservation': reservation.pk,
        }
        response = client.post('/api/contracts/', data)
        assert response.status_code == 201

    def test_contract_generate_pdf_endpoint(self, tenant_client, reservation):
        from apps.contracts.models import Contract
        client, tenant = tenant_client
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        response = client.get(f'/api/contracts/{contract.pk}/pdf/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_contract_sign_endpoint(self, tenant_client, reservation):
        from apps.contracts.models import Contract
        client, tenant = tenant_client
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            status='pending_signature',
        )
        data = {
            'signature': 'data:image/png;base64,iVBORw0KGgo...',
        }
        response = client.post(f'/api/contracts/{contract.pk}/sign/', data)
        assert response.status_code == 200
        contract.refresh_from_db()
        assert contract.status == 'signed'

    def test_contract_condition_report_create(self, tenant_client, reservation):
        from apps.contracts.models import Contract
        client, tenant = tenant_client
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        data = {
            'report_type': 'checkout',
            'fuel_level': 'full',
            'mileage': 15000,
            'exterior_condition': 'good',
            'interior_condition': 'good',
        }
        response = client.post(f'/api/contracts/{contract.pk}/condition-report/', data)
        assert response.status_code == 201

    def test_contract_download_endpoint(self, tenant_client, reservation):
        from apps.contracts.models import Contract
        client, tenant = tenant_client
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        response = client.get(f'/api/contracts/{contract.pk}/download/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert 'attachment' in response['Content-Disposition']


class TestConditionReportAPI:
    def test_condition_report_list(self, tenant_client, reservation):
        from apps.contracts.models import Contract, ConditionReport
        client, tenant = tenant_client
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        ConditionReport.objects.create(
            contract=contract,
            report_type='checkout',
            fuel_level='full',
            mileage=15000,
            exterior_condition='good',
            interior_condition='good',
        )
        response = client.get('/api/contracts/condition-reports/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_get_contract_condition_reports(self, tenant_client, reservation):
        from apps.contracts.models import Contract, ConditionReport
        client, tenant = tenant_client
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        ConditionReport.objects.create(
            contract=contract,
            report_type='checkout',
            fuel_level='full',
            mileage=15000,
            exterior_condition='good',
            interior_condition='good',
        )
        response = client.get(f'/api/contracts/{contract.pk}/condition-reports/')
        assert response.status_code == 200
        assert len(response.data) == 1


class TestContractPDFGeneration:
    def test_pdf_contains_customer_info(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            status='signed',
        )
        pdf_data = contract.generate_pdf()
        assert pdf_data is not None

    def test_pdf_contains_vehicle_info(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        pdf_data = contract.generate_pdf()
        assert pdf_data is not None

    def test_pdf_contains_rental_dates(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        pdf_data = contract.generate_pdf()
        assert pdf_data is not None

    def test_pdf_contains_pricing(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
        )
        pdf_data = contract.generate_pdf()
        assert pdf_data is not None

    def test_pdf_contains_terms(self, db, tenant, reservation):
        from apps.contracts.models import Contract
        terms = 'These are the standard rental terms...'
        contract = Contract.objects.create(
            tenant=tenant,
            reservation=reservation,
            terms_and_conditions=terms,
        )
        pdf_data = contract.generate_pdf()
        assert pdf_data is not None
