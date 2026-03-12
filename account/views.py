from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Citizen
from django.db.models import Count
from complaint.models import complaint
from schemes.models import Scheme
import random
from django.http import JsonResponse
import time
import requests
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

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
        # first_name = request.POST.get("full_name")
        email = request.POST.get('email')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        aadhaar = request.POST.get('aadhaar')
        ward = request.POST.get('ward')
        pincode = request.POST.get('pincode')
        village_name = request.POST.get('village')
        # village = Village.objects.filter(name=village_name).first()
        address = request.POST.get('address')
        district = request.POST.get("district")
        taluka = request.POST.get("taluka")
        village = request.POST.get("village")

        username = phone

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "User already registered with this phone number"
            })

        # Get full name from form
        
        first_name = request.POST.get("full_name")
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
            )
        
        # Save full name
        user.first_name = first_name
        user.save()

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
            district=district,
            taluka=taluka,
            village=village,
            ward=ward,
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

@login_required
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

    # 👇 NEW: pending schemes
    pending_schemes = Scheme.objects.filter(is_verified=False)

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved,
        "district_data": district_data,
        "department_data": department_data,
        "pending_schemes": pending_schemes
    }
    
    if request.user.userprofile.role != "super_admin":
        return redirect("homepage")

    return render(request,"super_admin_dashboard.html",context)

@login_required
def state_admin_dashboard(request):

    complaints = complaint.objects.all().order_by("-created_at")[:20]

    total = complaint.objects.count()

    pending = complaint.objects.filter(status="Pending").count()

    progress = complaint.objects.filter(status="In Progress").count()

    resolved = complaint.objects.filter(status="Resolved").count()

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

    # 👇 NEW: pending schemes
    pending_schemes = Scheme.objects.filter(is_verified=False)

    context = {
        "complaints": complaints,
        "total_complaints": total,
        "pending_complaints": pending,
        "progress_complaints": progress,
        "resolved_complaints": resolved,
        "district_data": district_data,
        "pending_schemes": pending_schemes
    }

    return render(request, "state_admin_dashboard.html", context)

def create_state_admin(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "create_state_admin.html", {
                "error": "Username already exists"
            })

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # assign state admin role
        UserProfile.objects.create(
            user=user,
            role="state_admin"
        )

        return redirect("super_admin_dashboard")

    return render(request, "create_state_admin.html")

@login_required
def edit_profile(request):

    # citizen = Citizen.objects.get(user=request.user)
    citizen, created = Citizen.objects.get_or_create(user=request.user)

    if request.method == "POST":

        # Update User fields
        request.user.first_name = request.POST.get("full_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        # Update Citizen fields
        citizen.phone = request.POST.get("phone")
        citizen.gender = request.POST.get("gender")
        citizen.aadhaar = request.POST.get("aadhaar")
        citizen.ward = request.POST.get("ward")

        village_name = request.POST.get("village")
        # village = Village.objects.filter(name=village_name).first()

        # citizen.village = village
        citizen.pincode = request.POST.get("pincode")
        citizen.address = request.POST.get("address")
        
        citizen.district = request.POST.get("district")
        citizen.taluka = request.POST.get("taluka")
        citizen.village = request.POST.get("village")

        citizen.save()

        return redirect("profile")

    return render(request, "edit_profile.html", {"citizen": citizen})

@login_required
def profile(request):
    return render(request, "userprofile.html")

@login_required
def verify_scheme(request, scheme_id):

    scheme = get_object_or_404(Scheme, id=scheme_id)

    scheme.is_verified = True
    scheme.save()

    return redirect(request.META.get('HTTP_REFERER'))