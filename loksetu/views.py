import logging
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

logger = logging.getLogger(__name__)


def send_email_to_client(first_name, last_name, email, message):
    """Helper to send contact email."""
    subject = "New Message from Client"
    full_message = f"Name: {first_name} {last_name}\nEmail: {email}\n\nMessage:\n{message}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.EMAIL_HOST_USER]  # or config("CONTACT_EMAIL")
    try:
        send_mail(subject, full_message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Contact email sent from {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send contact email: {e}")
        return False


def homepage(request):
    return render(request, "index.html")


def aboutus(request):
    return render(request, "aboutus.html")


def services(request):
    return render(request, "services.html")


def contactus(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if all([first_name, last_name, email, message]):
            if send_email_to_client(first_name, last_name, email, message):
                messages.success(request, "Your message was sent successfully!")
            else:
                messages.error(request, "Failed to send message. Please try again later.")
        else:
            messages.error(request, "Please fill in all fields.")
        return redirect("contactus")

    return render(request, "contact.html")


@login_required
def userprofile(request):
    return render(request, "profile.html")


def gallery(request):
    return render(request, "gallery.html")


def faq(request):
    return render(request, "faq.html")


def how_it_works(request):
    return render(request, "how_it_works.html")


def departments(request):
    return render(request, "departments.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def terms_conditions(request):
    return render(request, "terms_conditions.html")


def disclaimer(request):
    return render(request, "disclaimer.html")


def emergency_contacts(request):
    return render(request, "emergency_contacts.html")