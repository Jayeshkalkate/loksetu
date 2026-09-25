from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Document


class DocumentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc = Document.objects.create(
            title='RTI Application Form', category=Document.Category.FORM,
            external_link='https://maharashtra.gov.in/rti.pdf')

    def test_list_view(self):
        resp = self.client.get(reverse('documents'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'RTI Application Form')

    def test_url_property_prefers_file_then_link(self):
        self.assertEqual(self.doc.url, 'https://maharashtra.gov.in/rti.pdf')

    def test_clean_requires_file_or_link(self):
        d = Document(title='Bad doc', category=Document.Category.OTHER)
        with self.assertRaises(ValidationError):
            d.clean()

    def test_category_filter(self):
        resp = self.client.get(reverse('documents'), {'category': 'CIRCULAR'})
        self.assertNotContains(resp, 'RTI Application Form')
