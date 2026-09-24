import shutil
import tempfile

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from complaints.models import Complaint, Evidence, Status
from departments.models import Department, District

TMP_MEDIA = tempfile.mkdtemp()
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 32
PW = 'Str0ng-pass-phrase-77'


@override_settings(MEDIA_ROOT=TMP_MEDIA, SECURE_SSL_REDIRECT=False)
class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)
        cls.district = District.objects.get(name='Pune')
        cls.roads = Department.objects.get(name='Public Works')
        cls.water = Department.objects.get(name='Water Department')
        cls.citizen = User.objects.create_user('asha', 'asha@example.com', PW, first_name='Asha')
        cls.other = User.objects.create_user('ravi', 'ravi@example.com', PW)
        cls.officer = User.objects.create_user('off', 'off@example.com', PW, role='OFFICER', department=cls.roads)
        cls.dept_admin = User.objects.create_user('dadmin', 'da@example.com', PW, role='DEPT_ADMIN', department=cls.roads)
        cls.water_admin = User.objects.create_user('wadmin', 'wa@example.com', PW, role='DEPT_ADMIN', department=cls.water)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def make_complaint(self, **kw):
        from complaints.models import Category
        data = dict(citizen=self.citizen, category=Category.objects.get(name='Road damage'),
                    title='Pothole near school', description='A very deep pothole on the main road.',
                    district=self.district)
        data.update(kw)
        return Complaint.objects.create(**data)


class AccountTests(BaseCase):
    def test_staff_roles_get_staff_flag_and_group(self):
        self.assertTrue(self.officer.is_staff)
        self.assertEqual(list(self.officer.groups.values_list('name', flat=True)), ['Officers'])
        self.assertEqual(list(self.dept_admin.groups.values_list('name', flat=True)), ['Department Admins'])
        self.assertFalse(self.citizen.is_staff)

    def test_register_creates_citizen_and_logs_in(self):
        r = self.client.post(reverse('register'), {
            'username': 'newuser', 'first_name': 'New', 'last_name': 'User', 'email': 'new@example.com',
            'mobile': '+91 98765 43210', 'district': self.district.pk, 'password1': PW, 'password2': PW})
        self.assertRedirects(r, reverse('profile'))
        u = User.objects.get(username='newuser')
        self.assertEqual((u.role, u.mobile, u.is_staff), ('CITIZEN', '9876543210', False))

    def test_register_cannot_choose_role(self):
        self.client.post(reverse('register'), {
            'username': 'sneaky', 'first_name': 'S', 'email': 's@example.com', 'role': 'SUPER',
            'is_staff': 'on', 'password1': PW, 'password2': PW})
        u = User.objects.get(username='sneaky')
        self.assertEqual(u.role, 'CITIZEN')
        self.assertFalse(u.is_staff or u.is_superuser)

    def test_duplicate_email_and_bad_mobile_rejected(self):
        r = self.client.post(reverse('register'), {
            'username': 'dup', 'first_name': 'D', 'email': 'ASHA@example.com', 'mobile': '12345',
            'password1': PW, 'password2': PW})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='dup').exists())
        self.assertContains(r, 'already exists')
        self.assertContains(r, 'valid 10-digit')

    def test_login_keeps_next_and_logout_needs_post(self):
        r = self.client.post(reverse('login'), {'username': 'asha', 'password': PW, 'next': '/complaints/file/'})
        self.assertRedirects(r, '/complaints/file/')
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)

    def test_login_page_preserves_next(self):
        r = self.client.get(reverse('file_complaint'), follow=True)
        self.assertContains(r, 'name="next" value="/complaints/file/"')

    def test_login_is_throttled(self):
        for _ in range(20):
            self.client.post(reverse('login'), {'username': 'asha', 'password': 'wrong'})
        self.assertEqual(self.client.post(reverse('login'), {'username': 'asha', 'password': PW}).status_code, 429)

    def test_password_reset_sends_email(self):
        r = self.client.post(reverse('password_reset'), {'email': 'asha@example.com'})
        self.assertRedirects(r, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/reset/', mail.outbox[0].body)

    def test_profile_marks_notifications_read(self):
        c = self.make_complaint()
        c.record(self.citizen, 'x')
        self.client.force_login(self.citizen)
        self.assertContains(self.client.get(reverse('profile')), c.complaint_id)
        self.assertFalse(self.citizen.notification_set.filter(is_read=False).exists())


class ComplaintTests(BaseCase):
    form = None

    def payload(self, **kw):
        from complaints.models import Category
        d = {'category': Category.objects.get(name='Road damage').pk, 'title': 'Pothole',
             'description': 'A very deep pothole on the main road.', 'district': self.district.pk,
             'incident_date': '2026-01-01'}
        d.update(kw)
        return d

    def test_requires_login(self):
        self.assertEqual(self.client.get(reverse('file_complaint')).status_code, 302)

    def test_file_complaint_routes_department_and_stores_evidence(self):
        self.client.force_login(self.citizen)
        with self.captureOnCommitCallbacks(execute=True):
            r = self.client.post(reverse('file_complaint'),
                                 self.payload(evidence=SimpleUploadedFile('p.png', PNG, 'image/png')))
        c = Complaint.objects.get()
        self.assertRedirects(r, reverse('complaint_detail', args=[c.complaint_id]))
        self.assertRegex(c.complaint_id, r'^LKS-MH-\d{4}-\d{6}$')
        self.assertEqual(c.department, self.roads)
        self.assertEqual(c.evidence.count(), 1)
        self.assertEqual(c.history.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_fake_file_content_rejected(self):
        self.client.force_login(self.citizen)
        r = self.client.post(reverse('file_complaint'),
                             self.payload(evidence=SimpleUploadedFile('evil.png', b'<script>alert(1)</script>', 'image/png')))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'does not match')
        self.assertEqual(Complaint.objects.count(), 0)

    def test_bad_extension_and_oversize_rejected(self):
        self.client.force_login(self.citizen)
        r = self.client.post(reverse('file_complaint'),
                             self.payload(evidence=SimpleUploadedFile('a.exe', b'MZ', 'application/octet-stream')))
        self.assertContains(r, 'Allowed files')
        big = SimpleUploadedFile('big.pdf', b'%PDF-' + b'0' * (10 * 1024 * 1024 + 1), 'application/pdf')
        self.assertContains(self.client.post(reverse('file_complaint'), self.payload(evidence=big)), '10 MB')

    def test_validation_rules(self):
        self.client.force_login(self.citizen)
        for bad, msg in [({'description': 'short'}, 'more detail'),
                         ({'incident_date': '2999-01-01'}, 'future'),
                         ({'latitude': '95', 'longitude': '10'}, 'less than or equal to 90'),
                         ({'latitude': '18.5'}, 'both latitude and longitude')]:
            self.assertContains(self.client.post(reverse('file_complaint'), self.payload(**bad)), msg)
        self.assertEqual(Complaint.objects.count(), 0)

    def test_public_view_hides_private_details(self):
        c = self.make_complaint(title='Secret title 9 Main St', description='Private description text')
        r = self.client.get(reverse('complaint_detail', args=[c.complaint_id]))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'Secret title')
        self.assertNotContains(r, 'Private description')
        self.assertContains(r, 'Road damage')

    def test_owner_and_scoped_staff_see_details(self):
        c = self.make_complaint(title='Secret title', assigned_to=self.officer)
        url = reverse('complaint_detail', args=[c.complaint_id])
        for u, visible in [(self.citizen, True), (self.dept_admin, True), (self.officer, True),
                           (self.other, False), (self.water_admin, False)]:
            self.client.force_login(u)
            self.assertEqual('Secret title' in self.client.get(url).content.decode(), visible, u.username)

    def test_unassigned_officer_cannot_see_details(self):
        c = self.make_complaint(title='Secret title')
        self.client.force_login(self.officer)
        self.assertNotContains(self.client.get(reverse('complaint_detail', args=[c.complaint_id])), 'Secret title')

    def test_evidence_access_control(self):
        c = self.make_complaint()
        e = Evidence.objects.create(complaint=c, file=SimpleUploadedFile('p.png', PNG, 'image/png'))
        url = reverse('evidence_file', args=[e.pk])
        self.assertEqual(self.client.get(url).status_code, 404)  # anonymous
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)  # other citizen
        self.client.force_login(self.water_admin)
        self.assertEqual(self.client.get(url).status_code, 404)  # other department
        self.client.force_login(self.citizen)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'image/png')
        self.assertEqual(r['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(b''.join(r.streaming_content), PNG)
        self.client.force_login(self.dept_admin)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_track_found_missing_and_throttled(self):
        c = self.make_complaint()
        r = self.client.get(reverse('track'), {'id': c.complaint_id.lower()})
        self.assertRedirects(r, reverse('complaint_detail', args=[c.complaint_id]))
        self.assertContains(self.client.get(reverse('track'), {'id': 'LKS-MH-2026-999999'}), 'No complaint found')
        for _ in range(30):
            self.client.get(reverse('track'), {'id': 'LKS-MH-2026-999999'})
        self.assertEqual(self.client.get(reverse('track'), {'id': 'X'}).status_code, 429)

    def test_history_only_lists_own(self):
        self.make_complaint()
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(reverse('history')), 'LKS-MH')

    def test_status_change_notifies_and_emails(self):
        c = self.make_complaint()
        with self.captureOnCommitCallbacks(execute=True):
            c.set_status(Status.RESOLVED, self.officer, 'Fixed')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(self.citizen.notification_set.filter(message__contains='Resolved').exists())

    def test_map_data_is_public_safe(self):
        self.make_complaint(latitude=18.52043, longitude=73.85674, title='Secret title')
        self.make_complaint()  # no coordinates -> excluded
        d = self.client.get(reverse('map_data')).json()
        self.assertEqual(len(d['points']), 1)
        self.assertEqual(set(d['points'][0]), {'lat', 'lng', 'status', 'category'})
        self.assertEqual((d['points'][0]['lat'], d['points'][0]['lng']), (18.52, 73.86))


class AdminScopeTests(BaseCase):
    def test_department_scoping(self):
        c = self.make_complaint(assigned_to=self.officer)
        self.client.force_login(self.dept_admin)
        self.assertContains(self.client.get('/admin/complaints/complaint/'), c.complaint_id)
        self.client.force_login(self.water_admin)
        self.assertNotContains(self.client.get('/admin/complaints/complaint/'), c.complaint_id)
        self.client.force_login(self.officer)
        self.assertContains(self.client.get('/admin/complaints/complaint/'), c.complaint_id)

    def test_officer_cannot_edit_citizen_fields(self):
        c = self.make_complaint(assigned_to=self.officer)
        self.client.force_login(self.officer)
        r = self.client.post(f'/admin/complaints/complaint/{c.pk}/change/', {
            'status': 'RESOLVED', 'title': 'HACKED', 'description': 'HACKED',
            'assigned_to': '', 'history-TOTAL_FORMS': 0, 'history-INITIAL_FORMS': 0,
            'evidence-TOTAL_FORMS': 0, 'evidence-INITIAL_FORMS': 0})
        c.refresh_from_db()
        self.assertEqual((c.status, c.title, c.assigned_to), ('RESOLVED', 'Pothole near school', self.officer))
        self.assertEqual(c.history.count(), 1)

    def test_bulk_action_records_history(self):
        c = self.make_complaint()
        su = User.objects.create_superuser('root', 'r@example.com', PW)
        self.client.force_login(su)
        self.client.post('/admin/complaints/complaint/', {
            'action': 'mark_resolved', '_selected_action': [c.pk]})
        c.refresh_from_db()
        self.assertEqual(c.status, Status.RESOLVED)
        self.assertEqual(c.history.count(), 1)


class PublicPageTests(BaseCase):
    def test_pages_render(self):
        for name in ('home', 'about', 'contact', 'schemes', 'departments', 'news', 'emergency',
                     'privacy', 'terms', 'disclaimer', 'login', 'register', 'track', 'complaint_map',
                     'password_reset'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_healthz_and_robots(self):
        self.assertEqual(self.client.get('/healthz/').content, b'ok')
        self.assertContains(self.client.get('/robots.txt'), 'Disallow: /admin/')

    def test_seed_is_idempotent_and_has_no_placeholder_content(self):
        call_command('seed', verbosity=0)
        self.assertEqual(District.objects.count(), 36)
        from schemes.models import Scheme
        self.assertEqual(Scheme.objects.count(), 0)
        call_command('seed', '--demo', verbosity=0)
        self.assertEqual(Scheme.objects.count(), 1)

    def test_footer_hides_unset_social_links(self):
        self.assertNotContains(self.client.get(reverse('home')), 'Connect with me')
        with override_settings(SOCIAL_LINKS={'github': 'https://github.com/x', 'linkedin': ''}):
            r = self.client.get(reverse('home'))
        self.assertContains(r, 'https://github.com/x')

    @override_settings(DEBUG=False)
    def test_custom_404(self):
        self.assertContains(self.client.get('/nope/'), 'Page not found', status_code=404)
