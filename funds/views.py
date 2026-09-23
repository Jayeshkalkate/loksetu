import json
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models, transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from account.permissions import role_required
from .forms import FundForm, ProjectForm, LocationForm
from .models import Fund, Project, Location

logger = logging.getLogger(__name__)


# -------------------- Helper --------------------
def _get_fund_stats():
    """Aggregate fund statistics."""
    total_funds = Fund.objects.aggregate(total=models.Sum('total_amount'))['total'] or 0
    total_released = Fund.objects.aggregate(total=models.Sum('released_amount'))['total'] or 0
    total_used = Project.objects.aggregate(total=models.Sum('used_amount'))['total'] or 0
    return {
        'total_funds': total_funds,
        'total_released': total_released,
        'total_used': total_used,
        'remaining': total_funds - total_used,
    }


# -------------------- Dashboard --------------------
@login_required
@role_required(['super_admin', 'state_officer', 'district_officer'])
def dashboard(request):
    """Main dashboard with fund summary and lists."""
    funds_list = Fund.objects.select_related('location').prefetch_related('projects').all()
    paginator = Paginator(funds_list, 15)
    page = request.GET.get('page')
    try:
        funds = paginator.page(page)
    except PageNotAnInteger:
        funds = paginator.page(1)
    except EmptyPage:
        funds = paginator.page(paginator.num_pages)

    stats = _get_fund_stats()
    context = {
        'funds': funds,
        'locations': Location.objects.all(),
        **stats,
    }
    return render(request, 'funds/dashboard.html', context)


# -------------------- Fund CRUD --------------------
@login_required
@role_required(['super_admin', 'state_officer'])
def fund_create(request):
    if request.method == 'POST':
        form = FundForm(request.POST)
        if form.is_valid():
            fund = form.save()
            messages.success(request, f'Fund "{fund.title}" created successfully.')
            return redirect('funds:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FundForm()
    return render(request, 'funds/fund_form.html', {'form': form, 'action': 'Create'})


@login_required
@role_required(['super_admin', 'state_officer'])
def fund_edit(request, pk):
    fund = get_object_or_404(Fund, pk=pk)
    if request.method == 'POST':
        form = FundForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fund "{fund.title}" updated successfully.')
            return redirect('funds:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FundForm(instance=fund)
    return render(request, 'funds/fund_form.html', {'form': form, 'action': 'Edit'})


@login_required
@role_required(['super_admin'])
@require_http_methods(['POST'])
def fund_delete(request, pk):
    fund = get_object_or_404(Fund, pk=pk)
    title = fund.title
    fund.delete()
    messages.success(request, f'Fund "{title}" deleted successfully.')
    return redirect('funds:dashboard')


# -------------------- Project CRUD --------------------
@login_required
@role_required(['super_admin', 'state_officer'])
def project_create(request, fund_pk=None):
    initial = {}
    if fund_pk:
        initial['fund'] = get_object_or_404(Fund, pk=fund_pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('funds:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(initial=initial)
    return render(request, 'funds/project_form.html', {'form': form, 'action': 'Create'})


@login_required
@role_required(['super_admin', 'state_officer'])
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully.')
            return redirect('funds:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'funds/project_form.html', {'form': form, 'action': 'Edit'})


@login_required
@role_required(['super_admin'])
@require_http_methods(['POST'])
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    name = project.name
    project.delete()
    messages.success(request, f'Project "{name}" deleted successfully.')
    return redirect('funds:dashboard')


# -------------------- Location CRUD --------------------
@login_required
@role_required(['super_admin'])
def location_create(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save()
            messages.success(request, f'Location "{location.name}" created.')
            return redirect('funds:dashboard')
    else:
        form = LocationForm()
    return render(request, 'funds/location_form.html', {'form': form})


@login_required
@role_required(['super_admin'])
def location_edit(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, f'Location "{location.name}" updated.')
            return redirect('funds:dashboard')
    else:
        form = LocationForm(instance=location)
    return render(request, 'funds/location_form.html', {'form': form})


@login_required
@role_required(['super_admin'])
@require_http_methods(['POST'])
def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    name = location.name
    location.delete()
    messages.success(request, f'Location "{name}" deleted.')
    return redirect('funds:dashboard')


# -------------------- Bulk Upload --------------------
@login_required
@role_required(['super_admin'])
@transaction.atomic
def bulk_upload(request):
    if request.method != 'POST':
        return render(request, 'funds/bulk_upload.html')

    file = request.FILES.get('file')
    if not file:
        messages.error(request, 'No file selected.')
        return redirect('funds:bulk_upload')

    if not file.name.endswith('.json'):
        messages.error(request, 'Only JSON files are allowed.')
        return redirect('funds:bulk_upload')

    try:
        data = json.load(file)
    except json.JSONDecodeError as e:
        messages.error(request, f'Invalid JSON file: {e}')
        return redirect('funds:bulk_upload')

    if not isinstance(data, list):
        messages.error(request, 'JSON must contain a list of objects.')
        return redirect('funds:bulk_upload')

    created_count = 0
    updated_count = 0
    errors = []

    for idx, item in enumerate(data, start=1):
        # Validate required fields
        required = ['title', 'year', 'location']
        if not all(k in item for k in required):
            errors.append(f"Row {idx}: Missing required fields: {required}")
            continue

        # Get or create location
        location_name = item['location']
        location, loc_created = Location.objects.get_or_create(
            name=location_name,
            defaults={'type': Location.DISTRICT}  # default type; you can adjust
        )
        if loc_created:
            # Optionally log location creation
            pass

        # Prepare fund data
        defaults = {
            'department': item.get('department', ''),
            'total_amount': item.get('total_amount', 0),
            'released_amount': item.get('released_amount', 0),
        }

        try:
            fund, created = Fund.objects.update_or_create(
                title=item['title'],
                year=item['year'],
                location=location,
                defaults=defaults
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")

    if errors:
        messages.warning(request, f"Bulk upload completed with {len(errors)} errors. "
                                  f"Created: {created_count}, Updated: {updated_count}. "
                                  f"First error: {errors[0]}")
    else:
        messages.success(request, f"Bulk upload successful. Created: {created_count}, Updated: {updated_count}")

    return redirect('funds:dashboard')


# -------------------- API (optional) --------------------
@login_required
def fund_detail_json(request, pk):
    fund = get_object_or_404(Fund, pk=pk)
    data = {
        'id': fund.id,
        'title': fund.title,
        'department': fund.department,
        'total_amount': str(fund.total_amount),
        'released_amount': str(fund.released_amount),
        'used_amount': str(fund.used_amount),
        'remaining': str(fund.remaining_amount),
        'year': fund.year,
        'location': fund.location.name,
        'projects': [{'id': p.id, 'name': p.name, 'status': p.status} for p in fund.projects.all()],
    }
    return JsonResponse(data)