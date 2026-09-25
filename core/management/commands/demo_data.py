"""
Loads a full, realistic-looking demo dataset across every app: users of every role,
complaints spread across statuses/districts/categories/dates (so dashboard charts have
something to show), schemes, news, projects, funds, documents, reports, FAQs and
support tickets.

This is for LOCAL DEVELOPMENT / DEMOS ONLY. Every record is clearly prefixed
"[DEMO]" so it's easy to spot and to bulk-delete later. Safe to re-run: it uses
get_or_create keyed by name/username, so running it twice will not create duplicates
(though complaint counts are deliberately re-checked by a marker, see below).

Usage (after the base `seed` command and `migrate`):
    python manage.py demo_data
    python manage.py demo_data --flush   # remove all [DEMO] data first, then reload
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from complaints.models import Category, Complaint, Status, StatusHistory
from departments.models import Department, District
from documents.models import Document
from faq.models import FAQ
from funds.models import Fund
from news.models import Announcement
from projects.models import Project
from reports.models import Report
from schemes.models import Scheme
from support.models import SupportTicket

User = get_user_model()
DEMO_PASSWORD = 'Demo-pass-2026!'
TAG = '[DEMO] '


class Command(BaseCommand):
    help = 'Load a full demo dataset (users, complaints, schemes, projects, funds, documents, reports, FAQ, support tickets).'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='Delete all previously loaded [DEMO] data first, then reload.')

    def handle(self, *a, flush=False, **k):
        call_command('seed')  # make sure districts/departments/categories/emergency numbers exist

        if flush:
            self.flush_demo_data()

        districts = list(District.objects.all())
        categories = list(Category.objects.select_related('department').all())
        if not districts or not categories:
            self.stderr.write(self.style.ERROR('No districts/categories found even after seed(); aborting.'))
            return

        users = self.make_users()
        self.make_complaints(users, districts, categories)
        self.make_schemes()
        self.make_news()
        self.make_projects(districts)
        self.make_funds()
        self.make_documents()
        self.make_reports()
        self.make_faqs()
        self.make_support_tickets(users)

        self.stdout.write(self.style.SUCCESS(
            f'Demo data loaded. Citizen/officer/admin login password for all [DEMO] users: {DEMO_PASSWORD}'))

    # ---------------------------------------------------------------- helpers

    def flush_demo_data(self):
        Complaint.objects.filter(title__startswith=TAG).delete()
        SupportTicket.objects.filter(subject__startswith=TAG).delete()
        Scheme.objects.filter(name__startswith=TAG).delete()
        Announcement.objects.filter(title__startswith=TAG).delete()
        Project.objects.filter(name__startswith=TAG).delete()
        Fund.objects.filter(name__startswith=TAG).delete()
        Document.objects.filter(title__startswith=TAG).delete()
        Report.objects.filter(title__startswith=TAG).delete()
        FAQ.objects.filter(question__startswith=TAG).delete()
        User.objects.filter(username__startswith='demo_').delete()
        self.stdout.write('Flushed previous [DEMO] data.')

    def make_users(self):
        users = {'citizens': [], 'officers': [], 'dept_admins': [], 'super': None}
        districts = list(District.objects.all())
        for i in range(1, 6):
            u, _ = User.objects.get_or_create(
                username=f'demo_citizen{i}',
                defaults={'email': f'demo.citizen{i}@example.com',
                         'district': random.choice(districts) if districts else None})
            u.set_password(DEMO_PASSWORD)
            u.save()
            users['citizens'].append(u)

        depts = list(Department.objects.all())
        for i, dept in enumerate(depts[:4], start=1):
            officer, _ = User.objects.get_or_create(
                username=f'demo_officer{i}',
                defaults={'email': f'demo.officer{i}@example.com', 'role': User.Role.OFFICER, 'department': dept})
            officer.set_password(DEMO_PASSWORD)
            officer.role = User.Role.OFFICER
            officer.department = dept
            officer.save()
            users['officers'].append(officer)

            admin, _ = User.objects.get_or_create(
                username=f'demo_deptadmin{i}',
                defaults={'email': f'demo.deptadmin{i}@example.com', 'role': User.Role.DEPT_ADMIN, 'department': dept})
            admin.set_password(DEMO_PASSWORD)
            admin.role = User.Role.DEPT_ADMIN
            admin.department = dept
            admin.save()
            users['dept_admins'].append(admin)

        superuser, _ = User.objects.get_or_create(
            username='demo_superadmin', defaults={'email': 'demo.super@example.com', 'role': User.Role.SUPER})
        superuser.set_password(DEMO_PASSWORD)
        superuser.role = User.Role.SUPER
        superuser.save()
        users['super'] = superuser
        return users

    def make_complaints(self, users, districts, categories):
        # Idempotency guard: only (re)build the demo complaint set if it isn't already there.
        if Complaint.objects.filter(title__startswith=TAG).count() >= 40:
            return
        titles = [
            'Pothole near main road', 'No water supply for 3 days', 'Streetlight not working',
            'Garbage not collected', 'Frequent power cuts', 'Open manhole is a safety hazard',
            'Blocked drainage causing flooding', 'Illegal dumping near school',
            'Broken footpath tiles', 'Water pipeline leakage', 'Transformer sparking',
            'Stray animal menace', 'Encroachment on public road', 'Damaged bus stop shelter',
        ]
        statuses = list(Status.choices)
        now = timezone.now()
        created_count = 0
        for i in range(60):
            cat = random.choice(categories)
            district = random.choice(districts)
            citizen = random.choice(users['citizens'])
            status_code, _ = random.choice(statuses)
            days_ago = random.randint(0, 55)
            title = f'{TAG}{random.choice(titles)} #{i + 1}'

            complaint = Complaint.objects.create(
                citizen=citizen, category=cat, title=title,
                description=f'Demo complaint auto-generated for dashboard/testing purposes. Category: {cat.name}.',
                district=district, status=status_code,
                incident_date=(now - timedelta(days=days_ago)).date(),
            )
            # Backdate `created`/`updated` (auto_now[_add] fields ignore assignment on .save(),
            # so update() directly against the DB instead).
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            updated_at = created_at + timedelta(days=random.randint(0, min(days_ago, 10)))
            Complaint.objects.filter(pk=complaint.pk).update(created=created_at, updated=updated_at)

            if status_code not in (Status.SUBMITTED,):
                officer = next((o for o in users['officers'] if o.department_id == complaint.department_id), None)
                if officer:
                    Complaint.objects.filter(pk=complaint.pk).update(assigned_to=officer)
                StatusHistory.objects.create(complaint=complaint, status=status_code,
                                             note='Demo timeline entry.', changed_by=officer)
            created_count += 1
        self.stdout.write(f'Created {created_count} demo complaints.')

    def make_schemes(self):
        depts = list(Department.objects.all())
        samples = [
            ('Rural Housing Assistance Scheme', 'Financial assistance for rural housing construction.'),
            ('Farmer Crop Insurance Scheme', 'Subsidized crop insurance for registered farmers.'),
            ('Girl Child Education Grant', 'Scholarship support for girl children in government schools.'),
            ('Senior Citizen Pension Scheme', 'Monthly pension for eligible senior citizens.'),
            ('Skill Development Program', 'Vocational training for unemployed youth.'),
        ]
        for name, desc in samples:
            Scheme.objects.get_or_create(
                name=f'{TAG}{name}',
                defaults={'description': desc, 'official_source': 'https://www.maharashtra.gov.in',
                         'department': random.choice(depts) if depts else None})

    def make_news(self):
        samples = [
            ('New online grievance portal launched', 'Citizens can now track complaints in real time.'),
            ('Monsoon preparedness advisory', 'District administrations issue flood preparedness guidelines.'),
            ('Road repair drive across districts', 'Public Works Department announces pothole-repair drive.'),
            ('Water conservation awareness week', 'Department urges citizens to conserve water this summer.'),
            ('Digital literacy camps announced', 'Free digital literacy camps for rural citizens.'),
        ]
        for title, body in samples:
            Announcement.objects.get_or_create(title=f'{TAG}{title}', defaults={'body': body})

    def make_projects(self, districts):
        depts = list(Department.objects.all())
        samples = [
            ('Highway widening project', Project.Status.ONGOING, 250.5),
            ('Rural water pipeline extension', Project.Status.PLANNED, 45.0),
            ('Smart streetlight installation', Project.Status.COMPLETED, 18.75),
            ('Flood control embankment', Project.Status.DELAYED, 90.2),
            ('Solid waste processing plant', Project.Status.ONGOING, 60.0),
            ('Riverfront beautification', Project.Status.PLANNED, 32.4),
        ]
        for name, status, budget in samples:
            Project.objects.get_or_create(
                name=f'{TAG}{name}',
                defaults={'description': f'Demo project entry ({status.label}).', 'status': status,
                         'budget_crore': budget, 'department': random.choice(depts) if depts else None,
                         'district': random.choice(districts),
                         'official_source': 'https://www.maharashtra.gov.in'})

    def make_funds(self):
        depts = list(Department.objects.all())
        samples = [
            ('Rural Roads Development Fund', '2024-25', 150, 140),
            ('Rural Roads Development Fund', '2025-26', 180, 60),
            ('Drinking Water Mission Fund', '2025-26', 220, 95),
            ('Education Infrastructure Fund', '2025-26', 90, 30),
            ('Disaster Relief Fund', '2025-26', 300, 210),
        ]
        for name, year, allocated, utilized in samples:
            Fund.objects.get_or_create(
                name=f'{TAG}{name}', financial_year=year,
                defaults={'allocated_crore': allocated, 'utilized_crore': utilized,
                         'department': random.choice(depts) if depts else None,
                         'official_source': 'https://www.maharashtra.gov.in'})

    def make_documents(self):
        samples = [
            ('RTI application form', Document.Category.FORM),
            ('Circular on grievance redressal timelines', Document.Category.CIRCULAR),
            ('Notification: revised complaint categories', Document.Category.NOTIFICATION),
            ('Guideline for filing evidence with complaints', Document.Category.GUIDELINE),
            ('Annual citizen charter', Document.Category.OTHER),
        ]
        for title, category in samples:
            Document.objects.get_or_create(
                title=f'{TAG}{title}',
                defaults={'category': category, 'external_link': 'https://www.maharashtra.gov.in',
                         'description': 'Demo document entry.'})

    def make_reports(self):
        samples = [
            ('Annual Performance Report 2025', Report.ReportType.ANNUAL),
            ('Complaint Resolution Audit', Report.ReportType.AUDIT),
            ('Citizen Satisfaction Survey', Report.ReportType.SURVEY),
            ('Departmental Performance Review', Report.ReportType.PERFORMANCE),
            ('Grievance Redressal Study', Report.ReportType.OTHER),
        ]
        for title, rtype in samples:
            Report.objects.get_or_create(
                title=f'{TAG}{title}',
                defaults={'report_type': rtype, 'summary': 'Demo report entry.',
                         'external_link': 'https://www.maharashtra.gov.in'})

    def make_faqs(self):
        samples = [
            ('Getting started', 'How do I file a complaint?', 'Log in, then use "File a complaint" from the menu.'),
            ('Getting started', 'Do I need to create an account?', 'Yes, an account lets you track your complaints.'),
            ('Complaints', 'How long does resolution take?', 'It depends on the department and category.'),
            ('Complaints', 'Can I upload photos as evidence?', 'Yes, JPG, PNG, PDF and MP4 files up to 10 MB.'),
            ('Complaints', 'How do I track my complaint?', 'Use the Track a complaint page with your complaint ID.'),
            ('Account', 'How do I reset my password?', 'Use the password reset link on the login page.'),
            ('Account', 'Can I change my registered mobile number?', 'Update it from your profile page.'),
        ]
        for i, (category, question, answer) in enumerate(samples, start=1):
            FAQ.objects.get_or_create(question=f'{TAG}{question}',
                                      defaults={'category': category, 'answer': answer, 'order': i})

    def make_support_tickets(self, users):
        samples = [
            'Cannot upload evidence photo', "Email notifications aren't arriving",
            'Request to merge duplicate account', 'Feedback on new dashboard', 'Site is slow on mobile',
        ]
        statuses = [SupportTicket.Status.OPEN, SupportTicket.Status.IN_PROGRESS,
                   SupportTicket.Status.RESOLVED, SupportTicket.Status.CLOSED]
        for i, subject in enumerate(samples):
            citizen = users['citizens'][i % len(users['citizens'])]
            SupportTicket.objects.get_or_create(
                user=citizen, subject=f'{TAG}{subject}',
                defaults={'message': 'Demo support ticket auto-generated for testing.',
                         'status': statuses[i % len(statuses)]})
