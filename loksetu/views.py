from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

def send_email_to_client(first_name, last_name, email, message):
    subject = "New Message from Client"
    full_message = f"Name: {first_name} {last_name}\nEmail: {email}\n\nMessage:\n{message}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["jayeshkalkate432@gmail.com"]
    send_mail(subject, full_message, from_email, recipient_list)

@login_required
def homepage(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, "aboutus.html")

def services(request):
    return render(request, "services.html")

def contactus(request):
    return render(request, "contact.html")


@login_required(login_url='login')
def contactus(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if first_name and last_name and email and message:
            send_email_to_client(first_name, last_name, email, message)
            messages.success(request, "Email sent successfully!")
            return redirect('contactus')
        else:
            messages.error(request, "Please fill in all fields.")
            return redirect('contactus')

    return render(request, "contact.html")

def userprofile(request):
    return render(request, "userprofile.html")

def gallery(request):
    return render(request, "gallery.html")

def faq(request):
    return render(request, "faq.html")

def how_it_works(request):
    return render(request, "how_it_works.html")

def departments(request):
    return render(request, "departments.html")

def post(request):
    return render(request, "post.html")

def singlepost(request):
    return render(request, "singlepost.html")

def privacy_policy(request):
    return render(request, "privacy_policy.html")

def terms_conditions(request):
    return render(request, "terms_conditions.html")

def disclaimer(request):
    return render(request, "disclaimer.html")

def emergency_contacts(request):
    return render(request, "emergency_contacts.html")

def singlepost(request):
    return render(request, "singlepost.html")

def singlepost(request):
    return render(request, "singlepost.html")

