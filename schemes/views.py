import json
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from account.permissions import role_required
from .forms import SchemeForm, BulkUploadForm, SchemeSearchForm
from .models import Scheme

logger = logging.getLogger(__name__)


@login_required
def schemes(request):
    """Display schemes with pagination, search, and filtering."""
    # Only show verified schemes to non-staff users; staff see all.
    if request.user.is_staff:
        qs = Scheme.objects.all()
    else:
        qs = Scheme.objects.filter(is_verified=True)

    # Filter by user's state if not superuser (optional)
    # but we'll keep it for all users.

    search_form = SchemeSearchForm(request.GET or None)
    search_query = ''
    category_filter = ''
    level_filter = ''

    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search', '')
        category_filter = search_form.cleaned_data.get('category', '')
        level_filter = search_form.cleaned_data.get('level', '')

        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        if category_filter:
            qs = qs.filter(category=category_filter)
        if level_filter:
            qs = qs.filter(level=level_filter)

    # Split by level
    central = qs.filter(level='central')
    state = qs.filter(level='state')
    district = qs.filter(level='district')
    taluka = qs.filter(level='taluka')
    village = qs.filter(level='village')

    # Paginate each level separately
    def paginate(queryset, page_param, per_page=6):
        paginator = Paginator(queryset, per_page)
        page = request.GET.get(page_param, 1)
        try:
            return paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            return paginator.page(1)

    context = {
        'central': paginate(central, 'central_page'),
        'state': paginate(state, 'state_page'),
        'district': paginate(district, 'district_page'),
        'taluka': paginate(taluka, 'taluka_page'),
        'village': paginate(village, 'village_page'),
        'search_form': search_form,
        'search_query': search_query,
        'category': category_filter,
        'level': level_filter,
        'total_count': qs.count(),
    }
    return render(request, 'schemes/schemes.html', context)


@login_required
def scheme_detail(request, slug):
    scheme = get_object_or_404(Scheme, slug=slug)
    # Non-staff cannot see unverified schemes
    if not scheme.is_verified and not request.user.is_staff:
        messages.error(request, "This scheme is not yet verified.")
        return redirect('schemes:schemes')
    return render(request, 'schemes/scheme.html', {'scheme': scheme})


@login_required
@role_required(['super_admin', 'state_officer'])
def add_scheme(request):
    """Add a new scheme (staff only)."""
    if request.method == 'POST':
        form = SchemeForm(request.POST, request.FILES)
        if form.is_valid():
            scheme = form.save(commit=False)
            scheme.created_by = request.user
            scheme.is_verified = request.user.is_superuser  # auto-verify for superadmin
            scheme.save()
            messages.success(request, f"Scheme '{scheme.title}' added successfully.")
            return redirect('schemes:schemes')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchemeForm()
    return render(request, 'schemes/scheme', {'form': form})


@login_required
@role_required(['super_admin', 'state_officer'])
def edit_scheme(request, slug):
    scheme = get_object_or_404(Scheme, slug=slug)
    if request.method == 'POST':
        form = SchemeForm(request.POST, request.FILES, instance=scheme)
        if form.is_valid():
            form.save()
            messages.success(request, f"Scheme '{scheme.title}' updated.")
            return redirect('schemes:schemes')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchemeForm(instance=scheme)
    return render(request, 'schemes/scheme', {'form': form, 'edit': True})


@login_required
@role_required(['super_admin'])
@require_http_methods(['POST'])
def delete_scheme(request, slug):
    scheme = get_object_or_404(Scheme, slug=slug)
    title = scheme.title
    scheme.delete()
    messages.success(request, f"Scheme '{title}' deleted.")
    return redirect('schemes:schemes')


@login_required
@role_required(['super_admin'])
@require_http_methods(['POST'])
def verify_scheme(request, slug):
    scheme = get_object_or_404(Scheme, slug=slug)
    scheme.is_verified = True
    scheme.save()
    messages.success(request, f"Scheme '{scheme.title}' verified.")
    return redirect('schemes:schemes')


@login_required
@role_required(['super_admin'])
def bulk_upload(request):
    """Bulk upload schemes from JSON file."""
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                messages.error(request, f"Invalid JSON: {e}")
                return redirect('schemes:bulk_upload')

            if not isinstance(data, list):
                messages.error(request, "JSON must be a list of objects.")
                return redirect('schemes:bulk_upload')

            created_count = 0
            skipped_count = 0
            errors = []

            with transaction.atomic():
                for idx, item in enumerate(data, start=1):
                    title = item.get('title')
                    if not title:
                        skipped_count += 1
                        errors.append(f"Row {idx}: Missing 'title'")
                        continue

                    # Check if exists
                    if Scheme.objects.filter(title=title).exists():
                        skipped_count += 1
                        errors.append(f"Row {idx}: Scheme '{title}' already exists.")
                        continue

                    # Create scheme
                    try:
                        Scheme.objects.create(
                            title=title,
                            description=item.get('description', ''),
                            eligibility=item.get('eligibility', ''),
                            benefits=item.get('benefits', ''),
                            category=item.get('category', 'General'),
                            level=item.get('level', 'state'),
                            state=item.get('state', 'Maharashtra'),
                            district=item.get('district', ''),
                            taluka=item.get('taluka', ''),
                            village=item.get('village', ''),
                            official_link=item.get('official_link', ''),
                            created_by=request.user,
                            is_verified=request.user.is_superuser,  # auto-verify for superadmin
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"Row {idx}: {str(e)}")
                        skipped_count += 1

            if errors:
                messages.warning(request, f"Upload completed with {len(errors)} issues. "
                                          f"Created: {created_count}, Skipped: {skipped_count}. "
                                          f"First issue: {errors[0]}")
            else:
                messages.success(request, f"Upload successful. Created {created_count} schemes.")

            return redirect('schemes:schemes')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = BulkUploadForm()

    return render(request, 'schemes/bulk_upload.html', {'form': form})