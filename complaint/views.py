from django.shortcuts import render, redirect
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Complaint, ComplaintHistory

def resolve_Complaint(request, complaint_id):

    c = get_object_or_404(Complaint, complaint_id=complaint_id)

    c.status = "Resolved"
    c.save()
    
    ComplaintHistory.objects.create(
        complaint=c,
        status="Resolved",
        updated_by=request.user
    )

    return redirect("state_admin_dashboard")

def mark_Complaint_read(request, complaint_id):

    c = get_object_or_404(Complaint, complaint_id=complaint_id)

    c.status = "In Progress"
    c.save()
    
    ComplaintHistory.objects.create(
        complaint=c,
        status="Assigned",
        updated_by=request.user
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
            complaint=c,
            status="Submitted",
            updated_by=None
        )

        return redirect('Complaint_result', complaint_id=c.complaint_id)

    return render(request,"complaint.html")

# Complaint SECTION

def track_Complaint(request):

    Complaint_data = None

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")

        try:
            Complaint_data = Complaint.objects.get(complaint_id=complaint_id)
        except Complaint.DoesNotExist:
            Complaint_data = None

    return render(request, "track_complaint.html", {"Complaint": Complaint_data})


def Complaint_result(request, complaint_id):

    c = Complaint.objects.get(complaint_id=complaint_id)

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
            "complaint_id": c.complaint_id,
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

def close_Complaint(request, complaint_id):

    c = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )

    c.status = "Closed"
    c.save()
    
    ComplaintHistory.objects.create(
        complaint=c,
        status="Closed",
        updated_by=request.user
    )

    return redirect("state_admin_dashboard")

def Complaint_detail(request, complaint_id):

    c = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
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