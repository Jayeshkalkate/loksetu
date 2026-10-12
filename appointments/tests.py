from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment

User = get_user_model()
PW = 'Str0ng-pass-phrase-77'


class AppointmentCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)
        cls.user = User.objects.create_user('apptuser', 'appt@example.com', PW)
        cls.other = User.objects.create_user('apptother', 'apptother@example.com', PW)

    def create_appointment(self, user=None, **kwargs):
        date = timezone.localdate() + timedelta(days=2)
        data = dict(user=user or self.user, purpose='Discuss water connection', preferred_date=date,
                    preferred_time='10:00', notes='Please review the application.')
        data.update(kwargs)
        return Appointment.objects.create(**data)

    def test_owner_can_reschedule_pending_appointment(self):
        appointment = self.create_appointment()
        self.client.force_login(self.user)
        new_date = (timezone.localdate() + timedelta(days=3)).isoformat()
        response = self.client.post(reverse('appointment_edit', args=[appointment.appointment_id]), {
            'department': '', 'purpose': 'Discuss new water connection', 'preferred_date': new_date,
            'preferred_time': '11:30', 'notes': 'Updated notes.'})
        self.assertRedirects(response, reverse('appointment_detail', args=[appointment.appointment_id]))
        appointment.refresh_from_db()
        self.assertEqual(appointment.purpose, 'Discuss new water connection')
        self.assertEqual(appointment.preferred_time.strftime('%H:%M'), '11:30')

    def test_pending_appointment_can_be_cancelled_but_not_deleted(self):
        appointment = self.create_appointment()
        self.client.force_login(self.user)
        response = self.client.post(reverse('appointment_cancel', args=[appointment.appointment_id]))
        self.assertRedirects(response, reverse('appointment_list'))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)
        self.assertTrue(Appointment.objects.filter(pk=appointment.pk).exists())

    def test_cannot_manage_another_users_appointment(self):
        appointment = self.create_appointment(user=self.other)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('appointment_edit', args=[appointment.appointment_id])).status_code, 404)
        self.assertEqual(self.client.post(reverse('appointment_cancel', args=[appointment.appointment_id])).status_code, 404)

    def test_non_pending_appointment_cannot_be_rescheduled(self):
        appointment = self.create_appointment(status=Appointment.Status.CONFIRMED)
        self.client.force_login(self.user)
        response = self.client.get(reverse('appointment_edit', args=[appointment.appointment_id]))
        self.assertRedirects(response, reverse('appointment_detail', args=[appointment.appointment_id]))


    def test_department_admin_can_only_see_own_department_appointments(self):
        from departments.models import Department
        roads = Department.objects.get(name='Public Works')
        water = Department.objects.get(name='Water Department')
        admin = User.objects.create_user('wateradmin-appt', 'wateradmin-appt@example.com', PW,
                                         role='DEPT_ADMIN', department=water)
        water_case = self.create_appointment(department=water)
        road_case = self.create_appointment(department=roads, purpose='Report road issue')
        self.client.force_login(admin)
        response = self.client.get('/admin/appointments/appointment/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, water_case.appointment_id)
        self.assertNotContains(response, road_case.appointment_id)
