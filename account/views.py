import hashlib
import hmac
import json
import logging
import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from complaint.models import Complaint
from schemes.models import Scheme
from utils.email_service import send_email
from django.core.cache import cache
from utils.rate_limit import hit as rate_limit_hit

from .forms import (
    CitizenProfileForm,
    CustomAuthenticationForm,
    CustomUserCreationForm,
)
from .models import Citizen, UserProfile
from .permissions import role_required

logger = logging.getLogger(__name__)

OTP_MAX_SEND_PER_HOUR = 5
OTP_MAX_VERIFY_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300


def _hash_otp(otp, salt):
    """Never store the raw OTP — only a keyed hash, using SECRET_KEY as the key."""
    digest = hmac.new(settings.SECRET_KEY.encode(), f"{salt}:{otp}".encode(), hashlib.sha256)
    return digest.hexdigest()

# -------------------- Helpers --------------------
def _get_dashboard_stats():
    """Return aggregated complaint stats for dashboard."""
    total = Complaint.objects.count()
    pending = Complaint.objects.filter(status="Pending").count()
    progress = Complaint.objects.filter(status="In Progress").count()
    resolved = Complaint.objects.filter(status="Resolved").count()
    return {
        "total": total,
        "pending": pending,
        "progress": progress,
        "resolved": resolved,
        "status_chart": {"Pending": pending, "In Progress": progress, "Resolved": resolved},
    }


def _get_district_summary():
    """Return per-district complaint counts."""
    districts = (
        Complaint.objects.values("district")
        .annotate(
            total=Count("id"),
            pending=Count("id", filter=Q(status="Pending")),
            resolved=Count("id", filter=Q(status="Resolved")),
        )
        .order_by("district")
    )
    return list(districts)


def _get_department_summary():
    """Return per-department complaint counts."""
    departments = (
        Complaint.objects.values("department")
        .annotate(
            total=Count("id"),
            pending=Count("id", filter=Q(status="Pending")),
            resolved=Count("id", filter=Q(status="Resolved")),
        )
        .order_by("department")
    )
    return list(departments)


# -------------------- OTP Views --------------------
# OTPs are delivered by email (free via Gmail SMTP / console backend in
# dev — see settings.py) instead of a paid SMS gateway. The phone number
# is still the account identifier; the registration form already collects
# a required email address, which is where the OTP is sent.
@require_http_methods(["POST"])
def send_otp(request):
    """Generate an OTP, email it to the user, and store only a hash of it."""
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip()

    if not phone or not phone.isdigit() or len(phone) != 10:
        return JsonResponse({"status": "error", "message": "Enter a valid 10-digit phone number."})
    if not email:
        return JsonResponse({"status": "error", "message": "Enter your email address first."})

    # Per-session cooldown (resend spam)
    last_otp_time = request.session.get("otp_time", 0)
    if time.time() - last_otp_time < OTP_RESEND_COOLDOWN_SECONDS:
        wait = int(OTP_RESEND_COOLDOWN_SECONDS - (time.time() - last_otp_time))
        return JsonResponse(
            {"status": "error", "message": f"Please wait {wait} seconds before requesting another OTP."}
        )

    # Per-phone hourly cap (cache-backed, works across workers)
    if rate_limit_hit(f"otp:send:{phone}", OTP_MAX_SEND_PER_HOUR, 3600):
        return JsonResponse(
            {"status": "error", "message": "Too many OTP requests for this number. Try again later."}
        )

    otp = f"{secrets.randbelow(900000) + 100000}"
    salt = secrets.token_hex(8)

    request.session["otp_hash"] = _hash_otp(otp, salt)
    request.session["otp_salt"] = salt
    request.session["otp_phone"] = phone
    request.session["otp_email"] = email
    request.session["otp_time"] = int(time.time())
    request.session.pop("otp_verified", None)
    request.session.pop("otp_attempts", None)

    sent = send_email(
        subject="Your LokSetu verification code",
        message=(
            f"Your LokSetu OTP is {otp}. It is valid for "
            f"{getattr(settings, 'OTP_EXPIRY_SECONDS', 120) // 60} minutes. "
            "Do not share this code with anyone."
        ),
        recipient_list=[email],
        fail_silently=True,
    )

    if sent:
        return JsonResponse({"status": "success", "message": "OTP sent to your email."})

    if settings.DEBUG:
        # Console backend still "sends" successfully in dev; if this path is
        # hit it means email genuinely failed, so surface the OTP for testing.
        logger.info("DEBUG: OTP for %s / %s = %s", phone, email, otp)
        return JsonResponse({"status": "success", "message": f"Email failed. Use OTP: {otp} (debug only)"})

    return JsonResponse({"status": "error", "message": "Could not send OTP. Please try again later."})


@require_http_methods(["POST"])
def verify_otp(request):
    """Verify the OTP against its stored hash, with a bounded number of attempts."""
    phone = request.POST.get("phone", "").strip()
    entered_otp = request.POST.get("otp", "").strip()

    otp_hash = request.session.get("otp_hash")
    salt = request.session.get("otp_salt")
    session_phone = request.session.get("otp_phone")
    otp_time = request.session.get("otp_time")

    if not otp_hash or not session_phone:
        return JsonResponse({"status": "error", "message": "OTP session expired. Please request a new OTP."})

    attempts = request.session.get("otp_attempts", 0)
    if attempts >= OTP_MAX_VERIFY_ATTEMPTS:
        for key in ["otp_hash", "otp_salt", "otp_phone", "otp_email", "otp_time", "otp_attempts"]:
            request.session.pop(key, None)
        return JsonResponse(
            {"status": "error", "message": "Too many incorrect attempts. Please request a new OTP."}
        )

    expiry = getattr(settings, "OTP_EXPIRY_SECONDS", 120)
    if otp_time and time.time() - otp_time > expiry:
        for key in ["otp_hash", "otp_salt", "otp_phone", "otp_email", "otp_time", "otp_attempts"]:
            request.session.pop(key, None)
        return JsonResponse({"status": "error", "message": "OTP has expired. Please request a new one."})

    if phone == session_phone and hmac.compare_digest(_hash_otp(entered_otp, salt), otp_hash):
        request.session["otp_verified"] = True
        request.session.pop("otp_attempts", None)
        return JsonResponse({"status": "success", "message": "OTP verified."})

    request.session["otp_attempts"] = attempts + 1
    remaining = OTP_MAX_VERIFY_ATTEMPTS - (attempts + 1)
    return JsonResponse(
        {"status": "error", "message": f"Invalid OTP. {max(remaining, 0)} attempt(s) remaining."}
    )


# -------------------- Authentication Views --------------------
def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def login_view(request):
    """Login view with role-based redirection and brute-force lockout."""
    if request.user.is_authenticated:
        return redirect(_get_dashboard_for_user(request.user))

    form = CustomAuthenticationForm()
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        username = request.POST.get("username", "").strip()
        lockout_key = f"login:fail:{username}:{_client_ip(request)}"

        if (cache.get(lockout_key) or 0) >= LOGIN_MAX_ATTEMPTS:
            messages.error(
                request,
                "Too many failed login attempts. Please try again in a few minutes.",
            )
            return render(request, "login.html", {"form": form})

        if form.is_valid():
            # AuthenticationForm.clean() already authenticates internally;
            # form.get_user() returns that result without re-querying.
            cache.delete(lockout_key)
            login(request, form.get_user())
            return redirect(_get_dashboard_for_user(form.get_user()))
        else:
            # Wrong credentials (or a blank field) both land here since
            # AuthenticationForm validates the login itself in clean() —
            # count it as a failed attempt either way.
            try:
                cache.incr(lockout_key)
            except ValueError:
                cache.set(lockout_key, 1, timeout=LOGIN_LOCKOUT_SECONDS)
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {"form": form})


def register(request):
    """Registration view with OTP verification."""
    if request.user.is_authenticated:
        return redirect(_get_dashboard_for_user(request.user))

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # OTP must already have been verified via the /send-otp/ + /verify-otp/
            # AJAX flow (verify_otp sets otp_verified=True). We re-check phone
            # match and expiry here too, since session state is what we trust —
            # we never re-derive or compare the raw OTP again at this point.
            phone = form.cleaned_data.get("phone_number")

            session_phone = request.session.get("otp_phone")
            otp_time = request.session.get("otp_time")
            otp_verified = request.session.get("otp_verified", False)

            if not session_phone:
                messages.error(request, "OTP session expired. Please request a new OTP.")
                return render(request, "register.html", {"form": form})

            expiry = getattr(settings, "OTP_EXPIRY_SECONDS", 120)
            if otp_time and time.time() - otp_time > expiry:
                messages.error(request, "OTP has expired. Please resend.")
                return render(request, "register.html", {"form": form})

            if phone != session_phone:
                messages.error(request, "Phone number does not match the one OTP was sent to.")
                return render(request, "register.html", {"form": form})

            if not otp_verified:
                messages.error(request, "Please verify OTP first using the 'Verify OTP' button.")
                return render(request, "register.html", {"form": form})

            # Create user and citizen profile
            user = form.save(commit=False)
            user.username = phone  # use phone as username
            user.set_password(form.cleaned_data["password"])
            user.save()

            profile = UserProfile.objects.get(user=user)
            profile.role = "citizen"
            profile.save()

            Citizen.objects.create(
                user=user,
                phone=phone,
                gender=form.cleaned_data["gender"],
                aadhaar=form.cleaned_data["aadhaar"],
                district=form.cleaned_data["district"],
                taluka=form.cleaned_data["taluka"],
                village=form.cleaned_data["village"],
                ward=form.cleaned_data["ward"],
                pincode=form.cleaned_data["pincode"],
                address=form.cleaned_data["address"],
            )

            # Clean OTP session
            for key in ["otp_hash", "otp_salt", "otp_phone", "otp_email", "otp_time", "otp_verified", "otp_attempts"]:
                request.session.pop(key, None)

            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


# -------------------- Dashboard Views --------------------
def _get_dashboard_for_user(user):
    """Return the appropriate dashboard URL based on user role."""
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return "homepage"
    role = profile.role
    mapping = {
        "super_admin": "super_admin_dashboard",
        "state_officer": "state_dashboard",
        "district_officer": "district_dashboard",
        "taluka_officer": "taluka_dashboard",
        "village_officer": "village_dashboard",
        "citizen": "profile",
    }
    return mapping.get(role, "homepage")


@login_required
@role_required(["super_admin"])
def super_admin_dashboard(request):
    """Super admin dashboard with full statistics."""
    recent_complaints = Complaint.objects.select_related().order_by("-created_at")[:20]
    stats = _get_dashboard_stats()
    district_data = _get_district_summary()
    department_data = _get_department_summary()
    pending_schemes = Scheme.objects.filter(is_verified=False).select_related()

    context = {
        "complaints": recent_complaints,
        **stats,
        "district_data": district_data,
        "department_data": department_data,
        "pending_schemes": pending_schemes,
        "status_chart": json.dumps(stats["status_chart"]),
    }
    return render(request, "dashboard.html", context)


@login_required
@role_required(["state_officer"])
def state_dashboard(request):
    """State officer dashboard."""
    recent_complaints = Complaint.objects.select_related().order_by("-created_at")[:20]
    stats = _get_dashboard_stats()
    district_data = _get_district_summary()
    pending_schemes = Scheme.objects.filter(is_verified=False).select_related()

    context = {
        "complaints": recent_complaints,
        **stats,
        "district_data": district_data,
        "pending_schemes": pending_schemes,
    }
    return render(request, "dashboard/dashboard.html", context)


def _jurisdiction_dashboard(request, area_field, session_field_label):
    """Shared implementation for district/taluka/village officer dashboards:
    scope complaints and stats to the officer's assigned area instead of
    rendering a blank page."""
    profile = request.user.userprofile
    area_value = getattr(profile, area_field, None)

    if not area_value:
        messages.warning(
            request,
            f"No {session_field_label} has been assigned to your account yet. "
            "Contact a state officer or super admin to set it.",
        )
        complaints = Complaint.objects.none()
    else:
        filter_key = area_field.replace("assigned_", "")
        complaints = Complaint.objects.filter(**{filter_key: area_value}).order_by("-created_at")

    total = complaints.count()
    pending = complaints.filter(status="Pending").count()
    progress = complaints.filter(status="In Progress").count()
    resolved = complaints.filter(status="Resolved").count()

    context = {
        "complaints": complaints[:50],
        "total": total,
        "pending": pending,
        "progress": progress,
        "resolved": resolved,
        "area_value": area_value,
        "status_chart": json.dumps({"Pending": pending, "In Progress": progress, "Resolved": resolved}),
    }
    return render(request, "dashboard.html", context)


@login_required
@role_required(["district_officer"])
def district_dashboard(request):
    return _jurisdiction_dashboard(request, "assigned_district", "district")


@login_required
@role_required(["taluka_officer"])
def taluka_dashboard(request):
    return _jurisdiction_dashboard(request, "assigned_taluka", "taluka")


@login_required
@role_required(["village_officer"])
def village_dashboard(request):
    return _jurisdiction_dashboard(request, "assigned_village", "village")


# -------------------- Admin Management --------------------
@login_required
@role_required(["super_admin"])
def create_state_admin(request):
    """Create a new state officer account."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "dashboard.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "dashboard.html")

        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, "dashboard.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile.objects.get(user=user)
        profile.role = "state_officer"
        profile.save()

        messages.success(request, f"State officer '{username}' created successfully.")
        return redirect("super_admin_dashboard")

    return render(request, "dashboard.html")


@login_required
@role_required(["super_admin", "state_officer"])
def verify_scheme(request, scheme_id):
    """Mark a scheme as verified."""
    scheme = get_object_or_404(Scheme, id=scheme_id)
    if scheme.is_verified:
        messages.info(request, "Scheme is already verified.")
    else:
        scheme.is_verified = True
        scheme.save()
        messages.success(request, f"Scheme '{scheme.name}' verified successfully.")
    # Redirect to a known, safe destination based on the acting user's role
    # rather than trusting the client-supplied Referer header (open-redirect risk).
    return redirect(_get_dashboard_for_user(request.user))


# -------------------- Profile Views --------------------
@login_required
def profile(request):
    """Display user profile."""
    citizen = Citizen.objects.filter(user=request.user).first()
    return render(request, "profile.html", {"citizen": citizen})


@login_required
def edit_profile(request):
    """Edit citizen profile."""
    citizen, created = Citizen.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CitizenProfileForm(request.POST, instance=citizen, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CitizenProfileForm(instance=citizen, user=request.user)
    return render(request, "profile.html", {"form": form, "citizen": citizen})


# -------------------- Password Reset Placeholders --------------------
def password_reset_form(request):
    return render(request, "password.html")


def password_reset_confirm(request):
    return render(request, "password.html")


def password_reset_done(request):
    return render(request, "password.html")


def password_reset_complete(request):
    return render(request, "password.html")
