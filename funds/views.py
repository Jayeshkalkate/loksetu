from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib import messages
from .models import Fund, Project, Location
import json

# ==============================
# ROLE CHECK
# ==============================
from account.models import UserProfile

def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == "super_admin"
    except UserProfile.DoesNotExist:
        return False


def is_admin_or_state(user):
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role in ["super_admin", "state_admin"]
    except UserProfile.DoesNotExist:
        return False
    
# ==============================
# BULK UPLOAD
# ==============================
from django.db import transaction

@user_passes_test(is_admin)
@transaction.atomic
def funds_bulk_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')

        if not file or not file.name.endswith('.json'):
            return HttpResponse("Only JSON file allowed")

        try:
            data = json.load(file)
        except Exception:
            return HttpResponse("Invalid JSON file")

        for item in data:
            if not all(k in item for k in ["title", "year", "location"]):
                continue

            location, _ = Location.objects.get_or_create(
                name=item['location'],
                type='district'
            )

            Fund.objects.update_or_create(
                title=item['title'],
                year=item['year'],
                location=location,
                defaults={
                    'department': item.get('department', ''),
                    'total_amount': item.get('total_amount', 0),
                    'released_amount': item.get('released_amount', 0),
                }
            )

        messages.success(request, "Bulk upload successful")
        return redirect('/')

    return redirect('/?view=upload')

# ==============================
# DASHBOARD
# ==============================
@login_required
def dashboard(request):
    view_type = request.GET.get('view', 'dashboard')

    funds = Fund.objects.select_related('location').prefetch_related('projects')
    projects = Project.objects.select_related('fund')
    projects = Project.objects.all()
    locations = Location.objects.all()

    total_funds = funds.aggregate(total=Sum('total_amount'))['total'] or 0
    total_released = funds.aggregate(total=Sum('released_amount'))['total'] or 0
    total_used = projects.aggregate(total=Sum('used_amount'))['total'] or 0

    context = {
        'view_type': view_type,
        'funds': funds,
        'projects': projects,
        'locations': locations,
        'total_funds': total_funds,
        'total_released': total_released,
        'total_used': total_used,
        'remaining': total_funds - total_used,
    }

    if view_type == 'fund':
        fund = get_object_or_404(Fund, id=request.GET.get('id'))
        context.update({'fund': fund, 'projects': fund.projects.all()})

    if view_type == 'location':
        location = get_object_or_404(Location, id=request.GET.get('id'))
        context.update({
            'location': location,
            'funds': location.funds.all(),
            'projects': Project.objects.filter(fund__location=location)
        })

    return render(request, 'dashboard.html', context)

# ==============================
# CREATE
# ==============================
@user_passes_test(is_admin)
def create_fund(request):
    if request.method == 'POST':
        form = FundForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fund Created Successfully")
            return redirect('/')
    else:
        form = FundForm()

    return render(request, 'dashboard.html', {
        'view_type': 'create_fund',
        'form': form
    })

# ==============================
# EDIT
# ==============================
@user_passes_test(is_admin)
@user_passes_test(is_admin)
def edit_fund(request, id):
    fund = get_object_or_404(Fund, id=id)

    if request.method == 'POST':
        form = FundForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            messages.success(request, "Fund Updated")
            return redirect('/')
    else:
        form = FundForm(instance=fund)

    return render(request, 'dashboard.html', {
        'view_type': 'edit_fund',
        'form': form
    })

# ==============================
# DELETE
# ==============================
@user_passes_test(is_admin)
def delete_fund(request, id):
    fund = get_object_or_404(Fund, id=id)
    fund.delete()
    messages.success(request, "Fund Deleted")
    return redirect('/')