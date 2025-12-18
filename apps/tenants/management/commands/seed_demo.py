from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing demo data before creating new data',
        )

    def handle(self, *args, **options):
        from apps.tenants.models import Tenant, TenantUser
        from apps.fleet.models import Vehicle
        from apps.customers.models import Customer
        from apps.reservations.models import Reservation

        admin_email = 'admin@fleetflow.local'

        if options['reset']:
            self.stdout.write('Deleting existing demo data...')
            User.objects.filter(email=admin_email).delete()
            Tenant.objects.filter(slug='demo-rental').delete()

        # Create admin user (using email as identifier)
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write('Admin user already exists')

        # Create demo tenant
        tenant, created = Tenant.objects.get_or_create(
            slug='demo-rental',
            defaults={
                'name': 'Demo Car Rental',
                'owner': admin_user,
                'plan': 'professional',
                'business_name': 'Demo Car Rental Co.',
                'business_email': 'info@demo-rental.local',
                'business_phone': '555-DEMO',
                'business_address': '123 Demo Street, Austin, TX 78701',
                'vehicle_limit': 50,
                'user_limit': 10,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created demo tenant'))
        else:
            self.stdout.write('Demo tenant already exists')

        # Create tenant user relationship
        TenantUser.objects.get_or_create(
            tenant=tenant,
            user=admin_user,
            defaults={'role': 'owner'}
        )

        # Create sample vehicles
        vehicles_data = [
            {'make': 'Toyota', 'model': 'Camry', 'year': 2024, 'license_plate': 'DEMO-001', 'color': 'Silver', 'daily_rate': Decimal('55.00')},
            {'make': 'Honda', 'model': 'Accord', 'year': 2024, 'license_plate': 'DEMO-002', 'color': 'Black', 'daily_rate': Decimal('60.00')},
            {'make': 'Ford', 'model': 'Mustang', 'year': 2023, 'license_plate': 'DEMO-003', 'color': 'Red', 'daily_rate': Decimal('95.00')},
            {'make': 'Chevrolet', 'model': 'Tahoe', 'year': 2024, 'license_plate': 'DEMO-004', 'color': 'White', 'daily_rate': Decimal('120.00')},
            {'make': 'Tesla', 'model': 'Model 3', 'year': 2024, 'license_plate': 'DEMO-005', 'color': 'Blue', 'daily_rate': Decimal('110.00')},
        ]

        for i, v_data in enumerate(vehicles_data):
            vehicle, created = Vehicle.objects.get_or_create(
                tenant=tenant,
                license_plate=v_data['license_plate'],
                defaults={
                    'make': v_data['make'],
                    'model': v_data['model'],
                    'year': v_data['year'],
                    'vin': f'DEMO00000000000{i+1:02d}',
                    'color': v_data['color'],
                    'status': 'available',
                    'daily_rate': v_data['daily_rate'],
                    'mileage': 10000 + (i * 5000),
                }
            )
            if created:
                self.stdout.write(f'  Created vehicle: {v_data["make"]} {v_data["model"]}')

        # Create sample customers
        customers_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@example.com', 'phone': '555-0101'},
            {'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@example.com', 'phone': '555-0102'},
            {'first_name': 'Michael', 'last_name': 'Williams', 'email': 'mwilliams@example.com', 'phone': '555-0103'},
            {'first_name': 'Emily', 'last_name': 'Brown', 'email': 'emily.b@example.com', 'phone': '555-0104'},
            {'first_name': 'David', 'last_name': 'Garcia', 'email': 'dgarcia@example.com', 'phone': '555-0105'},
        ]

        customers = []
        for i, c_data in enumerate(customers_data):
            customer, created = Customer.objects.get_or_create(
                tenant=tenant,
                email=c_data['email'],
                defaults={
                    'first_name': c_data['first_name'],
                    'last_name': c_data['last_name'],
                    'phone': c_data['phone'],
                    'address': f'{100 + i} Main St, Austin, TX 78702',
                    'license_number': f'TX{12345678 + i}',
                    'license_state': 'TX',
                    'license_expiry': date.today() + timedelta(days=365 * 2),
                    'date_of_birth': date(1985 + i, (i % 12) + 1, (i % 28) + 1),
                }
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'  Created customer: {c_data["first_name"]} {c_data["last_name"]}')

        # Create sample reservations
        vehicles = list(Vehicle.objects.filter(tenant=tenant)[:3])
        if vehicles and customers:
            reservations_data = [
                {'customer': customers[0], 'vehicle': vehicles[0], 'days_from_now': 1, 'duration': 3, 'status': 'confirmed'},
                {'customer': customers[1], 'vehicle': vehicles[1], 'days_from_now': 5, 'duration': 7, 'status': 'confirmed'},
                {'customer': customers[2], 'vehicle': vehicles[2], 'days_from_now': -2, 'duration': 4, 'status': 'active'},
            ]

            for r_data in reservations_data:
                start_date = date.today() + timedelta(days=r_data['days_from_now'])
                end_date = start_date + timedelta(days=r_data['duration'])
                daily_rate = r_data['vehicle'].daily_rate
                total = daily_rate * r_data['duration']

                reservation, created = Reservation.objects.get_or_create(
                    tenant=tenant,
                    customer=r_data['customer'],
                    vehicle=r_data['vehicle'],
                    start_date=start_date,
                    defaults={
                        'end_date': end_date,
                        'status': r_data['status'],
                        'daily_rate': daily_rate,
                        'total_amount': total,
                    }
                )
                if created:
                    self.stdout.write(f'  Created reservation: {r_data["customer"]} - {r_data["vehicle"]}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write(f'  Email: {admin_email}')
        self.stdout.write(f'  Password: admin123')
        self.stdout.write(f'  URL: http://localhost:9091/dashboard/')
