from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Complaint, ComplaintHistory

def resolve_Complaint(request, Complaint_id):

    c = get_object_or_404(Complaint, Complaint_id=Complaint_id)

    c.status = "Resolved"
    c.save()
    
    ComplaintHistory.objects.create(
        Complaint=c,
        status="Resolved",
        updated_by="State Admin"
    )

    return redirect("state_admin_dashboard")

def mark_Complaint_read(request, Complaint_id):

    c = get_object_or_404(Complaint, Complaint_id=Complaint_id)

    c.status = "Assigned"
    c.save()
    
    ComplaintHistory.objects.create(
        Complaint=c,
        status="Assigned",
        updated_by="State Admin"
    )

    return redirect("state_admin_dashboard")

def Complaint_view(request):

    if request.method == "POST":

        c = Complaint.objects.create(

            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),

            gender=request.POST.get('gender'),
            aadhaar=request.POST.get('aadhaar'),

            state=request.POST.get('state'),
            district=request.POST.get('district'),
            taluka=request.POST.get('taluka'),
            village=request.POST.get('village'),
            ward=request.POST.get('ward'),
            pincode=request.POST.get('pincode'),

            department=request.POST.get('department'),

            title=request.POST.get('title'),
            description=request.POST.get('description'),

            issue_location=request.POST.get('issue_location'),
            issue_date=request.POST.get('issue_date'),

            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),

            evidence=request.FILES.get('evidence')
        )
        
        ComplaintHistory.objects.create(
            Complaint=c,
            status="Submitted",
            updated_by="Citizen"
        )

        return redirect('Complaint_result', Complaint_id=c.Complaint_id)

    return render(request,"complaint.html")

# Complaint SECTION

def track_Complaint(request):

    Complaint_data = None

    if request.method == "POST":
        Complaint_id = request.POST.get("Complaint_id")

        try:
            Complaint_data = Complaint.objects.get(Complaint_id=Complaint_id)
        except Complaint.DoesNotExist:
            Complaint_data = None

    return render(request, "track_complaint.html", {"Complaint": Complaint_data})


def Complaint_result(request, Complaint_id):

    c = Complaint.objects.get(Complaint_id=Complaint_id)

    return render(request, "Complaint_result.html", {"Complaint": c})

def map_Complaint(request):

    Complaints = Complaint.objects.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    )

    Complaint_data = []

    for c in Complaints:
        Complaint_data.append({
            "id": c.id,
            "Complaint_id": c.Complaint_id,
            "department": c.department,
            "status": c.status,
            "description": c.description,
            "latitude": c.latitude,
            "longitude": c.longitude
        })

    context = {
        "Complaint_json": json.dumps(Complaint_data)
        }
    
    return render(request, "map_complaint.html", context)

def close_Complaint(request, Complaint_id):

    c = get_object_or_404(
        Complaint,
        Complaint_id=Complaint_id
    )

    c.status = "Closed"
    c.save()

    ComplaintHistory.objects.create(
        Complaint=c,
        status="Closed",
        updated_by="Admin"
    )

    return redirect("state_admin_dashboard")

def Complaint_detail(request, Complaint_id):

    c = get_object_or_404(
        Complaint,
        Complaint_id=Complaint_id
    )

    history = c.history.all().order_by("timestamp")

    context = {
        "Complaint": c,
        "history": history
    }

    return render(
        request,
        "Complaint_detail.html",
        context
    )