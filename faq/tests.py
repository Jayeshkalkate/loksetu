from django.test import TestCase
from django.urls import reverse

from .models import FAQ


class FAQTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        FAQ.objects.create(category='Filing', question='How do I file a complaint?',
                           answer='Use the File a complaint page.', order=1)
        FAQ.objects.create(category='Filing', question='How long does it take?',
                           answer='It varies by department.', order=2)
        FAQ.objects.create(category='Account', question='How do I reset my password?',
                           answer='Use the password reset link on the login page.', order=1)

    def test_list_view_groups_by_category(self):
        resp = self.client.get(reverse('faq'))
        self.assertEqual(resp.status_code, 200)
        grouped = dict(resp.context['grouped'])
        self.assertEqual(set(grouped.keys()), {'Filing', 'Account'})
        self.assertEqual(len(grouped['Filing']), 2)

    def test_list_view_shows_questions(self):
        resp = self.client.get(reverse('faq'))
        self.assertContains(resp, 'How do I file a complaint?')
        self.assertContains(resp, 'How do I reset my password?')
