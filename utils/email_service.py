import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# All email delivery goes through Django's EMAIL_BACKEND, which is either
# free Gmail SMTP or the console backend in development (see settings.py) —
# no paid transactional-email API is required anywhere in this module.


def send_email(
    subject,
    message,
    recipient_list,
    html_message=None,
    from_email=None,
    fail_silently=False,
):
    """
    Centralized email sender with logging.
    """
    if not recipient_list:
        logger.warning("No recipients provided for email: %s", subject)
        return False

    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=fail_silently,
        )
        if sent:
            logger.info("Email sent to %s: %s", recipient_list, subject)
        else:
            logger.warning("Email send returned 0 for %s", recipient_list)
        return sent
    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient_list, e)
        if not fail_silently:
            raise
        return False


def send_complaint_created_email(complaint):
    """
    Send confirmation email when a complaint is created.
    """
    if not complaint.email:
        logger.warning("No email for complaint %s, skipping notification", complaint.complaint_id)
        return False

    subject = f"Complaint Registered - {complaint.complaint_id}"
    context = {
        "full_name": complaint.full_name,
        "complaint_id": complaint.complaint_id,
        "title": complaint.title,
        "status": complaint.status,
        "created_at": complaint.created_at,
        "description": complaint.description[:200],
    }

    # Plain text fallback
    message = f"""
Hello {complaint.full_name},

Your complaint has been successfully registered.

Complaint ID: {complaint.complaint_id}
Title: {complaint.title}
Status: {complaint.status}
Date: {complaint.created_at}

Thank you for using LokSetu.
"""

    # You can optionally use HTML templates:
    # html_message = render_to_string('emails/complaint_created.html', context)
    html_message = None  # Set to HTML if templates exist

    return send_email(
        subject=subject,
        message=message,
        recipient_list=[complaint.email],
        html_message=html_message,
    )


def send_complaint_resolved_email(complaint):
    """
    Send notification when a complaint is resolved.
    """
    if not complaint.email:
        logger.warning("No email for complaint %s, skipping resolution notification", complaint.complaint_id)
        return False

    subject = f"Complaint Resolved - {complaint.complaint_id}"
    message = f"""
Hello {complaint.full_name},

Your complaint has been resolved.

Complaint ID: {complaint.complaint_id}
Title: {complaint.title}
Resolution Date: {complaint.updated_at}

Thank you for using LokSetu.
"""
    return send_email(
        subject=subject,
        message=message,
        recipient_list=[complaint.email],
    )


def send_new_scheme_email(user_email, scheme):
    """
    Notify a user about a new government scheme.
    """
    if not user_email:
        return False

    subject = f"New Government Scheme: {scheme.title}"
    message = f"""
A new government scheme has been added.

Scheme: {scheme.title}
Category: {scheme.category}
Level: {scheme.level}

Description:
{scheme.description}

For more details, visit LokSetu.
"""
    return send_email(
        subject=subject,
        message=message,
        recipient_list=[user_email],
    )


def send_bulk_scheme_notification(scheme, user_emails):
    """
    Send scheme notification to multiple users (bulk).
    """
    if not user_emails:
        return False

    subject = f"New Scheme: {scheme.title}"
    message = f"""
A new scheme '{scheme.title}' is now available on LokSetu.

Description:
{scheme.description}

Check it out now!
"""
    # For bulk, we send individually or use a service like Mailgun.
    # Here we send one by one (or you can chunk).
    for email in user_emails:
        send_email(subject=subject, message=message, recipient_list=[email])
    return True