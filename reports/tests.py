from django.test import TestCase
from django.urls import reverse

from .models import Report


class ReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.report = Report.objects.create(
            title='Annual Performance Report 2025', summary='Yearly summary.',
            report_type=Report.ReportType.ANNUAL, external_link='https://maharashtra.gov.in/report.pdf')

    def test_list_view(self):
        resp = self.client.get(reverse('reports'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Annual Performance Report 2025')

    def test_type_filter(self):
        resp = self.client.get(reverse('reports'), {'type': 'AUDIT'})
        self.assertNotContains(resp, 'Annual Performance Report 2025')

    def test_url_property(self):
        self.assertEqual(self.report.url, 'https://maharashtra.gov.in/report.pdf')
