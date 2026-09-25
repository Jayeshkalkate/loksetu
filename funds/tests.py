from django.test import TestCase
from django.urls import reverse

from .models import Fund


class FundTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fund = Fund.objects.create(
            name='Rural Roads Fund', financial_year='2025-26',
            allocated_crore=100, utilized_crore=25,
            official_source='https://maharashtra.gov.in')

    def test_list_view(self):
        resp = self.client.get(reverse('funds'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Rural Roads Fund')

    def test_utilization_percent(self):
        self.assertEqual(self.fund.utilization_percent, 25.0)

    def test_utilization_percent_zero_allocation(self):
        f = Fund(name='Zero fund', financial_year='2025-26', allocated_crore=0, utilized_crore=0)
        self.assertEqual(f.utilization_percent, 0)

    def test_year_filter(self):
        Fund.objects.create(name='Old fund', financial_year='2020-21', allocated_crore=10,
                            official_source='https://maharashtra.gov.in')
        resp = self.client.get(reverse('funds'), {'year': '2025-26'})
        self.assertContains(resp, 'Rural Roads Fund')
        self.assertNotContains(resp, 'Old fund')
