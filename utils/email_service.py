from django.core.mail import send_mail
from django.conf import settings


def send_complaint_created_email(complaint):
    if complaint.email:
        send_mail(
            subject=f"Complaint Registered - {complaint.complaint_id}",
            message=f"""
Hello {complaint.full_name},

Your complaint has been successfully registered.

Title: {complaint.title}

Status: {complaint.status}

Thank you for using LokSetu.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[complaint.email],
            fail_silently=True,
        )


def send_complaint_resolved_email(complaint):
    if complaint.email:
        send_mail(
            subject=f"Complaint Resolved - {complaint.complaint_id}",
            message=f"""
Hello {complaint.full_name},

Your complaint has been resolved.

Title: {complaint.title}

Thank you for using LokSetu.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[complaint.email],
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