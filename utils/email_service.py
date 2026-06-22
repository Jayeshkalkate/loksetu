from django.core.mail import send_mail
from django.conf import settings


def send_Complaint_created_email(Complaint):
    if Complaint.email:
        send_mail(
            subject=f"Complaint Registered - {Complaint.complaint_id}",
            message=f"""
Hello {Complaint.full_name},

Your Complaint has been successfully registered.

Title: {Complaint.title}

Status: {Complaint.status}

Thank you for using LokSetu.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[Complaint.email],
            fail_silently=True,
        )


def send_Complaint_resolved_email(Complaint):
    if Complaint.email:
        send_mail(
            subject=f"Complaint Resolved - {Complaint.complaint_id}",
            message=f"""
Hello {Complaint.full_name},

Your Complaint has been resolved.

Title: {Complaint.title}

Thank you for using LokSetu.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[Complaint.email],
            fail_silently=True,
        )


def send_new_scheme_email(user_email, scheme):
    send_mail(
        subject=f"New Government Scheme: {scheme.title}",
        message=f"""
A new government scheme has been added.

Scheme: {scheme.title}

Description:
{scheme.description}

Visit LokSetu for more details.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=True,
    )