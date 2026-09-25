from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import SupportTicket

User = get_user_model()
PW = 'Str0ng-pass-phrase-77'


class SupportTicketTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('supportuser', 'su@example.com', PW)

    def test_anonymous_cannot_access_support_form(self):
        resp = self.client.get(reverse('support'))
        self.assertEqual(resp.status_code, 302)

    def test_create_ticket(self):
        self.client.login(username='supportuser', password=PW)
        resp = self.client.post(reverse('support'), {
            'subject': 'Cannot log in', 'message': 'My password reset email never arrived.'})
        self.assertRedirects(resp, reverse('support_list'))
        ticket = SupportTicket.objects.get(subject='Cannot log in')
        self.assertEqual(ticket.user, self.user)
        self.assertTrue(ticket.ticket_id.startswith('LKS-SUP-'))
        self.assertEqual(ticket.status, SupportTicket.Status.OPEN)

    def test_user_only_sees_own_tickets(self):
        other = User.objects.create_user('other1', 'o1@example.com', PW)
        SupportTicket.objects.create(user=other, subject='Other issue', message='...')
        mine = SupportTicket.objects.create(user=self.user, subject='My issue', message='...')
        self.client.login(username='supportuser', password=PW)
        resp = self.client.get(reverse('support_list'))
        self.assertContains(resp, 'My issue')
        self.assertNotContains(resp, 'Other issue')

    def test_cannot_view_others_ticket_detail(self):
        other = User.objects.create_user('other2', 'o2@example.com', PW)
        ticket = SupportTicket.objects.create(user=other, subject='Private', message='...')
        self.client.login(username='supportuser', password=PW)
        resp = self.client.get(reverse('support_detail', args=[ticket.ticket_id]))
        self.assertEqual(resp.status_code, 404)
