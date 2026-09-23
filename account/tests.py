import re

from django.contrib.auth.models import User
from django.core import mail
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from .models import Citizen, UserProfile


class OTPFlowTests(TestCase):
    """Covers the email-based OTP flow that replaced the paid SMS gateway."""

    def test_send_otp_requires_valid_phone(self):
        response = self.client.post(reverse("send_otp"), {"phone": "123", "email": "a@example.com"})
        self.assertEqual(response.json()["status"], "error")

    def test_send_otp_requires_email(self):
        response = self.client.post(reverse("send_otp"), {"phone": "9876543210", "email": ""})
        self.assertEqual(response.json()["status"], "error")

    def test_send_otp_emails_the_code_and_never_returns_it(self):
        response = self.client.post(
            reverse("send_otp"), {"phone": "9876543210", "email": "citizen@example.com"}
        )
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertNotIn("OTP:", data["message"])  # raw OTP must never leak in the response (non-debug)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("citizen@example.com", mail.outbox[0].to)

    def test_verify_otp_locks_out_after_max_attempts(self):
        self.client.post(reverse("send_otp"), {"phone": "9876543210", "email": "citizen@example.com"})
        resp = None
        for _ in range(5):
            resp = self.client.post(reverse("verify_otp"), {"phone": "9876543210", "otp": "000000"})
        self.assertEqual(resp.json()["status"], "error")
        # A 6th attempt, even with correct info, should be locked out.
        resp = self.client.post(reverse("verify_otp"), {"phone": "9876543210", "otp": "000000"})
        self.assertIn("Too many", resp.json()["message"])

    def test_correct_otp_verifies(self):
        self.client.post(reverse("send_otp"), {"phone": "9876543210", "email": "citizen@example.com"})
        sent_body = mail.outbox[0].body
        otp = re.search(r"\b(\d{6})\b", sent_body).group(1)
        resp = self.client.post(reverse("verify_otp"), {"phone": "9876543210", "otp": otp})
        self.assertEqual(resp.json()["status"], "success")


class EncryptedAadhaarTests(TestCase):
    """Aadhaar must be encrypted at rest but transparently readable via the ORM."""

    def test_aadhaar_is_encrypted_in_the_database(self):
        user = User.objects.create_user(username="9876543211", password="Str0ngPass!23")
        citizen = Citizen.objects.create(
            user=user,
            phone="9876543211",
            aadhaar="123456789012",
            gender="Male",
            ward="1",
            pincode="411001",
            address="Test address",
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT aadhaar FROM account_citizen WHERE id = %s", [citizen.id])
            raw_value = cursor.fetchone()[0]
        self.assertNotEqual(raw_value, "123456789012")

        fetched = Citizen.objects.get(id=citizen.id)
        self.assertEqual(fetched.aadhaar, "123456789012")
        self.assertEqual(fetched.masked_aadhaar, "XXXX-XXXX-9012")


class LoginLockoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="9876543212", password="Str0ngPass!23")
        UserProfile.objects.get_or_create(user=self.user)

    def test_lockout_after_repeated_failures(self):
        for _ in range(5):
            self.client.post(reverse("login"), {"username": "9876543212", "password": "wrong"})
        response = self.client.post(
            reverse("login"), {"username": "9876543212", "password": "Str0ngPass!23"}
        )
        self.assertContains(response, "Too many failed login attempts")
