from datetime import date
from unittest.mock import patch

from django.db import connection
from django.test import TestCase
from django.urls import reverse

from .models import Complaint, ComplaintHistory


def _complaint_payload(**overrides):
    payload = {
        "full_name": "Test Citizen",
        "phone": "9876543210",
        "email": "citizen@example.com",
        "gender": "Male",
        "aadhaar": "123456789012",
        "state": "Maharashtra",
        "district": "Pune",
        "taluka": "Haveli",
        "village": "Wagholi",
        "ward": "3",
        "pincode": "412207",
        "department": "Water Supply",
        "title": "No water supply for a week",
        "description": "There has been no water supply in our locality for a week.",
        "issue_location": "Main Road, Wagholi",
        "issue_date": date.today().isoformat(),
    }
    payload.update(overrides)
    return payload


class ComplaintSubmissionTests(TestCase):
    def test_submitting_a_complaint_creates_a_history_entry(self):
        response = self.client.post(reverse("complaint:complaint"), _complaint_payload())
        self.assertEqual(Complaint.objects.count(), 1)
        complaint = Complaint.objects.first()
        self.assertEqual(ComplaintHistory.objects.filter(complaint=complaint).count(), 1)
        self.assertRedirects(
            response,
            reverse("complaint:complaint_result", args=[complaint.complaint_id]),
        )

    def test_complaint_id_format(self):
        self.client.post(reverse("complaint:complaint"), _complaint_payload())
        complaint = Complaint.objects.first()
        self.assertRegex(complaint.complaint_id, r"^LKS-MH-[0-9A-F]{8}$")

    def test_complaint_id_collision_is_retried_not_crashed(self):
        # Force uuid4 to return the same value twice in a row, then a third
        # (different) value — save() should retry rather than violate the
        # unique constraint or raise.
        import uuid as uuid_module

        fixed = uuid_module.UUID("11111111-1111-1111-1111-111111111111")
        varying = uuid_module.uuid4()

        with patch("complaint.models.uuid.uuid4", side_effect=[fixed, fixed, varying]):
            self.client.post(reverse("complaint:complaint"), _complaint_payload())
            self.client.post(reverse("complaint:complaint"), _complaint_payload(phone="9876543211"))

        self.assertEqual(Complaint.objects.count(), 2)
        ids = list(Complaint.objects.values_list("complaint_id", flat=True))
        self.assertEqual(len(ids), len(set(ids)))  # no duplicate IDs


class ComplaintTrackingTests(TestCase):
    def test_track_existing_complaint(self):
        self.client.post(reverse("complaint:complaint"), _complaint_payload())
        complaint = Complaint.objects.first()
        response = self.client.post(
            reverse("complaint:track_complaint"), {"complaint_id": complaint.complaint_id}
        )
        self.assertContains(response, complaint.complaint_id)

    def test_track_unknown_complaint_shows_error(self):
        response = self.client.post(
            reverse("complaint:track_complaint"), {"complaint_id": "LKS-MH-DEADBEEF"}
        )
        self.assertContains(response, "No complaint found")


class ComplaintAadhaarEncryptionTests(TestCase):
    def test_aadhaar_encrypted_at_rest(self):
        self.client.post(reverse("complaint:complaint"), _complaint_payload())
        complaint = Complaint.objects.first()

        with connection.cursor() as cursor:
            cursor.execute("SELECT aadhaar FROM complaint_complaint WHERE id = %s", [complaint.id])
            raw_value = cursor.fetchone()[0]
        self.assertNotEqual(raw_value, "123456789012")

        fetched = Complaint.objects.get(id=complaint.id)
        self.assertEqual(fetched.aadhaar, "123456789012")
        self.assertEqual(fetched.masked_aadhaar, "XXXX-XXXX-9012")
