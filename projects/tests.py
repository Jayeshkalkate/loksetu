from django.test import TestCase
from django.urls import reverse

from .models import Project


class ProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            name='Test Road Widening', description='Widening the highway.',
            status=Project.Status.ONGOING, official_source='https://maharashtra.gov.in')

    def test_list_view(self):
        resp = self.client.get(reverse('projects'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Road Widening')

    def test_list_view_filters_by_status(self):
        resp = self.client.get(reverse('projects'), {'status': 'COMPLETED'})
        self.assertNotContains(resp, 'Test Road Widening')

    def test_detail_view(self):
        resp = self.client.get(reverse('project_detail', args=[self.project.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Widening the highway.')

    def test_str_and_blurb(self):
        self.assertEqual(str(self.project), 'Test Road Widening')
        self.assertEqual(self.project.blurb, 'Widening the highway.')
