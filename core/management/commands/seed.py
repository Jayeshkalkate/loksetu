"""
Base production seed: creates the minimum reference data LOKSETU needs to run
(districts, departments, complaint categories, emergency helpline numbers).

This does NOT create any users, complaints, or other demo content — that is
what `demo_data` / `seed_demo` are for. Safe to re-run: everything uses
get_or_create keyed by name, so running it multiple times will not create
duplicates.

Usage:
    python manage.py seed
"""
from django.core.management.base import BaseCommand

from departments.models import Department, District
from complaints.models import Category
from emergency.models import EmergencyContact


class Command(BaseCommand):
    help = 'Seed base reference data: districts, departments, complaint categories, emergency contacts.'

    def handle(self, *args, **options):
        districts = self.seed_districts()
        departments = self.seed_departments()
        self.seed_categories(departments)
        self.seed_emergency()
        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {len(districts)} districts, {len(departments)} departments.'))

    def seed_districts(self):
        self.stdout.write('Seeding districts...')
        data = [
            dict(name='Pune', division='Pune Division', headquarters='Pune',
                 area_sq_km=15642, population=9429408, population_reference_year=2011,
                 talukas=15, villages=1868,
                 overview='One of the largest districts in Maharashtra, a major education, IT and automobile hub.'),
            dict(name='Mumbai Suburban', division='Konkan Division', headquarters='Bandra',
                 area_sq_km=446, population=9356962, population_reference_year=2011,
                 talukas=3, villages=0,
                 overview='Most densely populated district in the state, the commercial capital region.'),
            dict(name='Nagpur', division='Nagpur Division', headquarters='Nagpur',
                 area_sq_km=9892, population=4653570, population_reference_year=2011,
                 talukas=14, villages=1654,
                 overview='Winter capital of Maharashtra, an orange-trade and logistics hub.'),
            dict(name='Nashik', division='Nashik Division', headquarters='Nashik',
                 area_sq_km=15582, population=6107187, population_reference_year=2011,
                 talukas=15, villages=1930,
                 overview='Wine capital of India, known for grape cultivation and pilgrimage tourism.'),
            dict(name='Aurangabad', division='Aurangabad Division', headquarters='Chhatrapati Sambhajinagar',
                 area_sq_km=10100, population=3701282, population_reference_year=2011,
                 talukas=9, villages=1346,
                 overview='Historic city near Ajanta-Ellora, a growing industrial and tourism centre.'),
        ]
        objs = []
        for d in data:
            obj, _ = District.objects.get_or_create(name=d['name'], defaults=d)
            objs.append(obj)
        return objs

    def seed_departments(self):
        self.stdout.write('Seeding departments...')
        data = [
            dict(name='Public Works Department', category='URBAN',
                 description='Builds and maintains roads, bridges and government buildings.',
                 responsibilities='Road construction and repair\nBridge maintenance\nGovernment building upkeep',
                 citizen_helpline='1800-120-1234'),
            dict(name='Water Supply & Sanitation Department', category='URBAN',
                 description='Ensures clean drinking water supply and sanitation infrastructure.',
                 responsibilities='Piped water supply\nSewage treatment\nRural sanitation schemes',
                 citizen_helpline='1800-120-5678'),
            dict(name='Health & Family Welfare Department', category='HEALTH',
                 description='Runs public hospitals, health schemes and disease-control programmes.',
                 responsibilities='Primary health centres\nImmunisation drives\nHospital administration',
                 citizen_helpline='104'),
            dict(name='Education Department', category='EDU',
                 description='Oversees primary, secondary and higher education administration.',
                 responsibilities='School infrastructure\nTeacher recruitment\nScholarship schemes',
                 citizen_helpline='1800-120-9099'),
            dict(name='Agriculture Department', category='AGRI',
                 description='Supports farmers with schemes, subsidies and extension services.',
                 responsibilities='Crop insurance\nSeed and fertiliser subsidy\nIrrigation support',
                 citizen_helpline='1800-233-4000'),
            dict(name='Municipal Corporation (Solid Waste & Roads)', category='URBAN',
                 description='Handles local civic services: garbage collection, street lighting, local roads.',
                 responsibilities='Door-to-door garbage collection\nStreet light maintenance\nLocal road repair',
                 citizen_helpline='1800-102-2020'),
            dict(name='Social Welfare Department', category='WELFARE',
                 description='Implements welfare schemes for SC/ST/OBC and economically weaker sections.',
                 responsibilities='Scholarship disbursal\nHostel facilities\nPension schemes',
                 citizen_helpline='1800-120-8040'),
        ]
        objs = []
        for d in data:
            obj, _ = Department.objects.get_or_create(name=d['name'], defaults=d)
            objs.append(obj)
        return objs

    def seed_categories(self, departments):
        self.stdout.write('Seeding complaint categories...')
        by_name = {d.name: d for d in departments}
        data = [
            ('Pothole / Road damage', 'Public Works Department'),
            ('Streetlight not working', 'Municipal Corporation (Solid Waste & Roads)'),
            ('Garbage not collected', 'Municipal Corporation (Solid Waste & Roads)'),
            ('No water supply', 'Water Supply & Sanitation Department'),
            ('Sewage overflow', 'Water Supply & Sanitation Department'),
            ('Hospital service complaint', 'Health & Family Welfare Department'),
            ('School infrastructure issue', 'Education Department'),
            ('Crop insurance claim delay', 'Agriculture Department'),
            ('Pension not credited', 'Social Welfare Department'),
        ]
        cats = []
        for name, dept_name in data:
            dept = by_name.get(dept_name)
            if not dept:
                continue
            cat, _ = Category.objects.get_or_create(name=name, defaults=dict(department=dept))
            cats.append(cat)
        return cats

    def seed_emergency(self):
        self.stdout.write('Seeding emergency contacts...')
        data = [
            ('Police', 'Police Emergency', '100', 'All India police emergency helpline.'),
            ('Fire', 'Fire Brigade', '101', 'Fire emergency services.'),
            ('Ambulance', 'Medical Emergency', '108', 'Free emergency ambulance service.'),
            ('Disaster Management', 'State Disaster Helpline', '1077', 'Maharashtra state disaster management helpline.'),
            ('Women Safety', 'Women Helpline', '1091', '24x7 helpline for women in distress.'),
            ('Child Helpline', 'Child Helpline India', '1098', 'Helpline for children in need of care and protection.'),
        ]
        for category, name, number, description in data:
            EmergencyContact.objects.get_or_create(
                category=category, name=name, defaults=dict(number=number, description=description))