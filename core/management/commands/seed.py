from django.core.management.base import BaseCommand
from complaints.models import Category
from departments.models import Department, District
from documents.models import Document
from emergency.models import EmergencyContact
from faq.models import FAQ
from funds.models import Fund
from news.models import Announcement
from projects.models import Project
from reports.models import Report
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
            Project.objects.get_or_create(
                name='Sample project (replace with verified data)',
                defaults={'description': 'Placeholder entry. Add real projects with their official source.',
                          'official_source': 'https://www.maharashtra.gov.in'})
            Fund.objects.get_or_create(
                name='Sample fund (replace with verified data)', financial_year='2025-26',
                defaults={'allocated_crore': 0, 'official_source': 'https://www.maharashtra.gov.in'})
            Document.objects.get_or_create(
                title='Sample document (replace with verified data)',
                defaults={'external_link': 'https://www.maharashtra.gov.in'})
            Report.objects.get_or_create(
                title='Sample report (replace with verified data)',
                defaults={'summary': 'Placeholder entry.', 'external_link': 'https://www.maharashtra.gov.in'})
            FAQ.objects.get_or_create(
                question='How do I file a complaint?',
                defaults={'category': 'Getting started',
                          'answer': 'Log in, then use "File a complaint" from the menu.', 'order': 1})
        self.stdout.write(self.style.SUCCESS('Seed data loaded.'))
