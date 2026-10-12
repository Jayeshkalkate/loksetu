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


class SupportTicketCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('cruduser', 'crud@example.com', PW)
        cls.other = User.objects.create_user('crudother', 'crudother@example.com', PW)

    def test_open_ticket_can_be_edited_and_deleted(self):
        ticket = SupportTicket.objects.create(user=self.user, subject='Old subject', message='Original message')
        self.client.force_login(self.user)
        r = self.client.post(reverse('support_edit', args=[ticket.ticket_id]), {
            'subject': 'Updated subject', 'message': 'Updated support issue description.'})
        self.assertRedirects(r, reverse('support_detail', args=[ticket.ticket_id]))
        ticket.refresh_from_db()
        self.assertEqual(ticket.subject, 'Updated subject')
        r = self.client.post(reverse('support_delete', args=[ticket.ticket_id]))
        self.assertRedirects(r, reverse('support_list'))
        self.assertFalse(SupportTicket.objects.filter(pk=ticket.pk).exists())

    def test_ticket_crud_is_owner_scoped_and_status_restricted(self):
        ticket = SupportTicket.objects.create(user=self.other, subject='Private', message='Private ticket message')
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('support_edit', args=[ticket.ticket_id])).status_code, 404)
        ticket.user = self.user
        ticket.status = SupportTicket.Status.IN_PROGRESS
        ticket.save()
        self.assertRedirects(self.client.get(reverse('support_edit', args=[ticket.ticket_id])),
                             reverse('support_detail', args=[ticket.ticket_id]))
        self.assertEqual(self.client.post(reverse('support_delete', args=[ticket.ticket_id])).status_code, 302)
        self.assertTrue(SupportTicket.objects.filter(pk=ticket.pk).exists())
