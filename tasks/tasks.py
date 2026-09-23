import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list, html_message=None):
    """
    Celery task to send an email asynchronously.
    """
    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        if sent:
            logger.info("Email task sent to %s: %s", recipient_list, subject)
        else:
            logger.warning("Email task returned 0 for %s", recipient_list)
        return sent
    except Exception as exc:
        logger.error("Email task failed for %s: %s", recipient_list, exc)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries)


@shared_task
def send_complaint_created_email_task(complaint_id):
    """
    Send complaint creation email asynchronously.
    """
    from complaint.models import Complaint
    try:
        complaint = Complaint.objects.get(complaint_id=complaint_id)
    except Complaint.DoesNotExist:
        logger.error("Complaint %s not found for email task", complaint_id)
        return False

    from utils.email_service import send_complaint_created_email
    return send_complaint_created_email(complaint)


@shared_task
def send_complaint_resolved_email_task(complaint_id):
    """
    Send complaint resolved email asynchronously.
    """
    from complaint.models import Complaint
    try:
        complaint = Complaint.objects.get(complaint_id=complaint_id)
    except Complaint.DoesNotExist:
        logger.error("Complaint %s not found for resolved email", complaint_id)
        return False

    from utils.email_service import send_complaint_resolved_email
    return send_complaint_resolved_email(complaint)


@shared_task
def send_new_scheme_email_task(scheme_slug):
    """
    Send new scheme notification to all users asynchronously.
    """
    from schemes.models import Scheme
    try:
        scheme = Scheme.objects.get(slug=scheme_slug)
    except Scheme.DoesNotExist:
        logger.error("Scheme %s not found for email task", scheme_slug)
        return False

    from utils.email_service import send_new_scheme_email

    # Get all users with email (you may want to limit to active/subscribed)
    users = User.objects.exclude(email='')
    count = 0
    for user in users:
        sent = send_new_scheme_email(user.email, scheme)
        if sent:
            count += 1
    logger.info("Sent scheme notification to %d users", count)
    return count


@shared_task
def generate_report_task(report_type="daily"):
    """
    Generate a report (placeholder).
    """
    logger.info("Generating %s report...", report_type)
    # Actual report generation logic goes here
    return {"status": "success", "type": report_type}


@shared_task
def notify_officers_task(message, officer_roles=None):
    """
    Notify officers (placeholder - could send SMS/email).
    """
    if officer_roles is None:
        officer_roles = ["state_officer", "district_officer"]

    from account.models import UserProfile
    officer_users = UserProfile.objects.filter(role__in=officer_roles).select_related('user')
    emails = [up.user.email for up in officer_users if up.user.email]

    if not emails:
        logger.warning("No officer emails found for notification")
        return False

    subject = "LokSetu Officer Notification"
    message = f"{message}\n\n- LokSetu System"

    for email in emails:
        send_email_task.delay(subject, message, [email])

    logger.info("Officer notification sent to %d officers", len(emails))
    return True