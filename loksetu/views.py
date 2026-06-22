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

@login_required
def aboutus(request):
    return render(request, "aboutus.html")

@login_required
def services(request):
    return render(request, "services.html")

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

@login_required
def userprofile(request):
    return render(request, "userprofile.html")

@login_required
def gallery(request):
    return render(request, "gallery.html")

@login_required
def faq(request):
    return render(request, "faq.html")

@login_required
def how_it_works(request):
    return render(request, "how_it_works.html")

@login_required
def departments(request):
    return render(request, "departments.html")

@login_required
def post(request):
    return render(request, "post.html")

@login_required
def singlepost(request):
    return render(request, "singlepost.html")

@login_required
def privacy_policy(request):
    return render(request, "privacy_policy.html")

@login_required
def terms_conditions(request):
    return render(request, "terms_conditions.html")

@login_required
def disclaimer(request):
    return render(request, "disclaimer.html")

@login_required
def emergency_contacts(request):
    return render(request, "emergency_contacts.html")
