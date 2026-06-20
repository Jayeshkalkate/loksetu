from celery import shared_task

@shared_task
def send_email_task(email):
    print(f"Email sent to {email}")
    return True


@shared_task
def generate_report_task():
    print("Generating report...")
    return True


@shared_task
def notify_officers_task():
    print("Officer notification sent")
    return True