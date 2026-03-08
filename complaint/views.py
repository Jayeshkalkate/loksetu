from django.shortcuts import render, redirect
import json
from .models import complaint
from django.contrib import messages


def complaint_view(request):

    if request.method == "POST":

        c = complaint.objects.create(

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
        
        messages.success(request, "✅ Your complaint has been submitted successfully!")
        return redirect('complaint')   # reload same page
        # return render(request,"complaint_result.html",{"complaint":c})

    return render(request,"complaintw.html")

# complaint SECTION

def track_complaint(request):

    complaint_data = None

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")

        try:
            complaint_data = complaint.objects.get(id=complaint_id)
        except:
            complaint_data = None

    return render(request,"track_complaint.html",{"complaint":complaint_data})


def complaint_result(request):
    return render(request, "complaint_result.html")

def map_complaint(request):

    complaints = complaint.objects.all()

    complaint_data = []

    for c in complaints:
        complaint_data.append({
            "id": c.id,
            "department": c.department,
            "status": c.status,
            "description": c.description,
            "latitude": c.latitude,
            "longitude": c.longitude
        })

    context = {
        "complaint_json": json.dumps(complaint_data)
    }

    return render(request, "map_complaints.html", context)