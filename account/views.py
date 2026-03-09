from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Citizen
from django.db.models import Count
from complaint.models import complaint
import random
from django.http import JsonResponse
import time
import requests
        
def send_otp(request):

    if request.method == "POST":

        phone = request.POST.get("phone")

        if not phone:
            return JsonResponse({"status": "error", "message": "Phone required"})

        if not phone.isdigit() or len(phone) != 10:
            return JsonResponse({"status": "error", "message": "Invalid phone number"})

        otp = random.randint(100000, 999999)

        # Save OTP in session
        request.session["otp"] = str(otp)
        request.session["otp_phone"] = phone
        request.session["otp_time"] = int(time.time())

        # SMS API
        url = "https://www.fast2sms.com/dev/bulkV2"

        payload = {
            "sender_id": "FSTSMS",
            "message": f"Your LokSetu OTP is {otp}",
            "language": "english",
            "route": "q",
            "numbers": phone
        }

        headers = {
            "authorization": "YOUR_API_KEY",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        sms_sent = False

        try:
            response = requests.post(url, data=payload, headers=headers)
            result = response.json()
            print("Fast2SMS Response:", result)

            if result.get("return") == True:
                sms_sent = True

        except Exception as e:
            print("SMS API failed:", e)

        # Always print OTP in terminal
        print("Generated OTP:", otp)

        # If SMS fails, show OTP to user
        if not sms_sent:
            return JsonResponse({
                "status": "success",
                "message": f"SMS failed. Use this OTP for testing: {otp}"
            })

        return JsonResponse({
            "status": "success",
            "message": "OTP sent successfully"
        })

    return JsonResponse({"status": "error"})

def verify_otp(request):

    if request.method == "POST":

        phone = request.POST.get("phone")
        entered_otp = request.POST.get("otp")

        session_otp = request.session.get("otp")
        session_phone = request.session.get("otp_phone")
        otp_time = request.session.get("otp_time")

        if not session_otp or not session_phone:
            return JsonResponse({"status": "error", "message": "OTP expired"})

        if otp_time and time.time() - otp_time > 120:
            return JsonResponse({"status": "error", "message": "OTP expired"})

        if entered_otp == str(session_otp) and phone == session_phone:
            request.session["otp_verified"] = True
            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "error", "message": "Invalid OTP"})
    
def login_view(request):

    if request.method == "POST":
        
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            profile, created = UserProfile.objects.get_or_create(user=user)

            if profile.role == "super_admin":
                return redirect('super_admin_dashboard')

            elif profile.role == "state_admin":
                return redirect('state_admin_dashboard')

            elif profile.role == "district_admin":
                return redirect('district_admin_dashboard')

            elif profile.role == "taluka_admin":
                return redirect('taluka_admin_dashboard')

            elif profile.role == "village_admin":
                return redirect('village_admin_dashboard')

            else:
                return redirect('homepage')

    return render(request, "login.html")


def register(request):

    if request.method == "POST":

        phone = request.POST.get('phone_number')
        entered_otp = request.POST.get('otp')

        session_otp = request.session.get("otp")
        session_phone = request.session.get("otp_phone")
        otp_time = request.session.get("otp_time")

        # OTP existence check
        if not session_otp or not session_phone:
            return render(request, "register.html", {
                "error": "OTP expired. Please request a new OTP."
            })

        # OTP expiry check (2 minutes)
        if otp_time and time.time() - otp_time > 120:
            return render(request, "register.html", {
                "error": "OTP expired. Please resend OTP."
            })

        # OTP match check
        if entered_otp != str(session_otp) or phone != session_phone:
            return render(request, "register.html", {
                "error": "Invalid OTP"
            })
            
        # Check if OTP was verified using Verify OTP button
        if not request.session.get("otp_verified"):
            return render(request, "register.html", {
                "error": "Please verify OTP first."
                })

        # Get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        aadhaar = request.POST.get('aadhaar')
        ward = request.POST.get('ward')
        pincode = request.POST.get('pincode')
        village = request.POST.get('village')
        address = request.POST.get('address')

        username = phone

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "User already registered with this phone number"
            })

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role="citizen"
        )

        # Create citizen profile
        Citizen.objects.create(
            user=user,
            phone=phone,
            gender=gender,
            aadhaar=aadhaar,
            ward=ward,
            village=village,
            pincode=pincode,
            address=address
        )

        # Clear OTP session after successful registration
        request.session.pop("otp", None)
        request.session.pop("otp_phone", None)
        request.session.pop("otp_time", None)
        request.session.pop("otp_verified", None)

        return redirect('login')

    return render(request, "register.html")

def logout_view(request):

    logout(request)
    return redirect('login')


def password_reset_form(request):
    return render(request, "password_reset_form.html")


def password_reset_confirm(request):
    return render(request, "password_reset_confirm.html")


def password_reset_done(request):
    return render(request, "password_reset_done.html")


def password_reset_complete(request):
    return render(request, "password_reset_complete.html")


def super_admin_dashboard(request):

    complaints = complaint.objects.all().order_by("-created_at")[:20]

    total = complaint.objects.count()
    pending = complaint.objects.filter(status="Pending").count()
    progress = complaint.objects.filter(status="In Progress").count()
    resolved = complaint.objects.filter(status="Resolved").count()

    # district summary
    districts = complaint.objects.values("district").annotate(total=Count("id"))

    district_data = []

    for d in districts:
        district = d["district"]

        district_data.append({
            "district": district,
            "total": complaint.objects.filter(district=district).count(),
            "pending": complaint.objects.filter(district=district, status="Pending").count(),
            "resolved": complaint.objects.filter(district=district, status="Resolved").count(),
        })

    # department summary
    departments = complaint.objects.values("department").annotate(total=Count("id"))

    department_data = []

    for d in departments:
        dep = d["department"]

        department_data.append({
            "department": dep,
            "total": complaint.objects.filter(department=dep).count(),
            "pending": complaint.objects.filter(department=dep, status="Pending").count(),
            "resolved": complaint.objects.filter(department=dep, status="Resolved").count(),
        })

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved,
        "district_data": district_data,
        "department_data": department_data
    }

    return render(request,"super_admin_dashboard.html",context)


def state_admin_dashboard(request):

    complaints = complaint.objects.all().order_by("-created_at")[:20]

    total = complaint.objects.count()
    pending = complaint.objects.filter(status="Pending").count()
    progress = complaint.objects.filter(status="In Progress").count()
    resolved = complaint.objects.filter(status="Resolved").count()

    # district summary
    districts = complaint.objects.values("district").annotate(total=Count("id"))

    district_data = []

    for d in districts:
        district = d["district"]

        district_data.append({
            "district": district,
            "total": complaint.objects.filter(district=district).count(),
            "pending": complaint.objects.filter(district=district, status="Pending").count(),
            "resolved": complaint.objects.filter(district=district, status="Resolved").count(),
        })

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved,
        "district_data": district_data
    }

    return render(request,"state_admin_dashboard.html",context)

def district_admin_dashboard(request):

    # profile = UserProfile.objects.get(user=request.user)
    profile = UserProfile.objects.filter(user=request.user).first()

    complaints = complaint.objects.filter(
        district=profile.district
    )

    total = complaints.count()
    pending = complaints.filter(status="Pending").count()
    progress = complaints.filter(status="In Progress").count()
    resolved = complaints.filter(status="Resolved").count()

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved
    }

    return render(request,"district_admin_dashboard.html",context)


def taluka_admin_dashboard(request):

    profile = UserProfile.objects.get(user=request.user)

    complaints = complaint.objects.filter(
        taluka=profile.taluka
    )

    total = complaints.count()
    pending = complaints.filter(status="Pending").count()
    progress = complaints.filter(status="In Progress").count()
    resolved = complaints.filter(status="Resolved").count()

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved
    }

    return render(request,"taluka_admin_dashboard.html",context)


def village_admin_dashboard(request):

    profile = UserProfile.objects.get(user=request.user)

    complaints = complaint.objects.filter(
        village=profile.village
    )

    total = complaints.count()
    pending = complaints.filter(status="Pending").count()
    progress = complaints.filter(status="In Progress").count()
    resolved = complaints.filter(status="Resolved").count()

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved
    }

    return render(request,"village_admin_dashboard.html",context)