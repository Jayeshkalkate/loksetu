from django.core.management.base import BaseCommand
from complaints.models import Category
from departments.models import Department, District
from emergency.models import EmergencyContact
from news.models import Announcement
from schemes.models import Scheme

DISTRICTS = """Ahilyanagar,Akola,Amravati,Beed,Bhandara,Buldhana,Chandrapur,Chhatrapati Sambhajinagar,Dharashiv,
Dhule,Gadchiroli,Gondia,Hingoli,Jalgaon,Jalna,Kolhapur,Latur,Mumbai City,Mumbai Suburban,Nagpur,Nanded,
Nandurbar,Nashik,Palghar,Parbhani,Pune,Raigad,Ratnagiri,Sangli,Satara,Sindhudurg,Solapur,Thane,Wardha,
Washim,Yavatmal""".replace('\n', '').split(',')
CATEGORIES = {'Road damage': 'Public Works', 'Water supply': 'Water Department',
              'Street light': 'Municipal Authority', 'Garbage': 'Sanitation Department',
              'Electricity': 'Electricity Department', 'Public safety': 'Police / Emergency Department',
              'Drainage': 'Municipal Authority'}
EMERGENCY = [('Police', 'Police', '100'), ('Ambulance', 'Ambulance', '108'), ('Fire', 'Fire Brigade', '101'),
             ('All emergencies', 'National Emergency Number', '112'), ('Women', "Women's Helpline", '1091'),
             ('Child', 'Childline', '1098'), ('Cyber crime', 'Cyber Crime Helpline', '1930')]


class Command(BaseCommand):
    help = 'Load districts, departments, categories and emergency numbers (idempotent). Use --demo for sample content.'

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true',
                            help='Also add placeholder scheme/announcement (development only)')

    def handle(self, *a, demo=False, **k):
        for d in DISTRICTS:
            District.objects.get_or_create(name=d.strip())
        for cat, dept in CATEGORIES.items():
            dep, _ = Department.objects.get_or_create(name=dept)
            Category.objects.get_or_create(name=cat, defaults={'department': dep})
        for c, n, num in EMERGENCY:
            EmergencyContact.objects.get_or_create(number=num, defaults={'category': c, 'name': n})
        if demo:
            Scheme.objects.get_or_create(
                name='Sample scheme (replace with verified data)',
                defaults={'description': 'Placeholder entry. Add real schemes with their official source.',
                          'official_source': 'https://www.maharashtra.gov.in'})
            Announcement.objects.get_or_create(
                title='Welcome to LOKSETU',
                defaults={'body': 'Sample announcement. Only tick "official" for authoritative sources.'})
        self.stdout.write(self.style.SUCCESS('Seed data loaded.'))
