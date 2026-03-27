from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import Fund, Project, Location
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.role == 'admin'

@user_passes_test(is_admin)
def funds_bulk_upload(request):
    if request.method == 'POST':
        file = request.FILES['file']
        data = json.load(file)

        for item in data:
            try:
                location, _ = Location.objects.get_or_create(
                    name=item['location'],
                    type='district'
                    )
                
                Fund.objects.update_or_create(
                    title=item['title'],
                    year=item['year'],
                    defaults={
                        'department': item['department'],
                        'total_amount': item['total_amount'],
                        'released_amount': item['released_amount'],
                        'location': location,
                        }
                    )
                
            except Exception as e:
                print("Error:", e)
                
                return redirect('dashboard')
            
            return render(request, 'funds_bulk_upload.html')

# ==============================
# Dashboard View (Main)
# ==============================
@login_required
def dashboard(request):
    # 🔍 Filters (GET params)
    location_id = request.GET.get('location')
    year = request.GET.get('year')
    status = request.GET.get('status')

    funds = Fund.objects.all()
    projects = Project.objects.all()

    # 🎯 Apply Filters
    if location_id:
        funds = funds.filter(location_id=location_id)
        projects = projects.filter(fund__location_id=location_id)

    if year:
        funds = funds.filter(year=year)

    if status:
        projects = projects.filter(status=status)

    # 📊 Aggregations (SAFE way)
    total_funds = funds.aggregate(total=Sum('total_amount'))['total'] or 0
    total_released = funds.aggregate(total=Sum('released_amount'))['total'] or 0
    total_used = projects.aggregate(total=Sum('used_amount'))['total'] or 0

    remaining = total_funds - total_used

    # 📍 Location list for filter dropdown
    locations = Location.objects.all()

    # 📅 Available years (dynamic)
    years = Fund.objects.values_list('year', flat=True).distinct()

    context = {
        'funds': funds,
        'projects': projects,

        'total_funds': total_funds,
        'total_released': total_released,
        'total_used': total_used,
        'remaining': remaining,

        'locations': locations,
        'years': years,

        'selected_location': location_id,
        'selected_year': year,
        'selected_status': status,
    }

    return render(request, 'dashboard.html', context)


# ==============================
# Fund Detail View
# ==============================
@login_required
def fund_detail(request, fund_id):
    fund = get_object_or_404(Fund, id=fund_id)
    projects = fund.projects.all()

    context = {
        'fund': fund,
        'projects': projects,
    }

    return render(request, 'fund_detail.html', context)


# ==============================
# Project Detail View
# ==============================
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    proofs = project.proofs.all()
    complaints = project.complaints.all()

    context = {
        'project': project,
        'proofs': proofs,
        'complaints': complaints,
    }

    return render(request, 'project_detail.html', context)


# ==============================
# Location-wise View
# ==============================
@login_required
def location_detail(request, location_id):
    location = get_object_or_404(Location, id=location_id)

    funds = location.funds.all()
    projects = Project.objects.filter(fund__location=location)

    total_funds = funds.aggregate(total=Sum('total_amount'))['total'] or 0
    total_used = projects.aggregate(total=Sum('used_amount'))['total'] or 0

    context = {
        'location': location,
        'funds': funds,
        'projects': projects,
        'total_funds': total_funds,
        'total_used': total_used,
        'remaining': total_funds - total_used,
    }

    return render(request, 'location_detail.html', context)