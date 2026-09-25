from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
PW = 'Str0ng-pass-phrase-77'


class DashboardAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.citizen = User.objects.create_user('citizen1', 'c1@example.com', PW)
        cls.super_admin = User.objects.create_user('super1', 's1@example.com', PW, role='SUPER')

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.url)

    def test_citizen_redirected_to_profile(self):
        self.client.login(username='citizen1', password=PW)
        resp = self.client.get(reverse('dashboard'))
        self.assertRedirects(resp, reverse('profile'))

    def test_staff_sees_analytics_dashboard(self):
        self.client.login(username='super1', password=PW)
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dashboard/staff.html')
        self.assertIsNotNone(resp.context['site_counts'])

    def test_dept_admin_dashboard_is_scoped(self):
        from departments.models import Department
        dept = Department.objects.create(name='Test Dept')
        admin = User.objects.create_user('deptadmin1', 'da1@example.com', PW,
                                         role='DEPT_ADMIN', department=dept)
        self.client.login(username='deptadmin1', password=PW)
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['scoped'])
        self.assertIsNone(resp.context['site_counts'])
