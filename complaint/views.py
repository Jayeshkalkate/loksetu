import logging
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from account.permissions import role_required
from .forms import ComplaintForm, TrackComplaintForm
from .models import Complaint, ComplaintHistory

logger = logging.getLogger(__name__)


def complaint_view(request):
    """Public complaint submission page."""
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            # Save automatically generates complaint_id via model's save()
            complaint.save()

            # Log initial submission in history
            ComplaintHistory.objects.create(
                complaint=complaint,
                status="Submitted",
                updated_by=request.user if request.user.is_authenticated else None
            )

            messages.success(request, f'Complaint {complaint.complaint_id} submitted successfully.')
            return redirect('complaint:complaint_result', complaint_id=complaint.complaint_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComplaintForm()

    return render(request, 'complaint.html', {'form': form})


def complaint_result(request, complaint_id):
    """Show the result after submission."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    return render(request, 'complaint.html', {'complaint': complaint, 'submitted': True})


def track_complaint(request):
    """Track complaint status by ID."""
    tracked_complaint = None
    form = TrackComplaintForm()
    if request.method == 'POST':
        form = TrackComplaintForm(request.POST)
        if form.is_valid():
            complaint_id = form.cleaned_data['complaint_id']
            try:
                tracked_complaint = Complaint.objects.get(complaint_id=complaint_id)
            except Complaint.DoesNotExist:
                messages.error(request, 'No complaint found with that ID.')
        else:
            messages.error(request, 'Invalid complaint ID format.')

    return render(
        request,
        'complaint.html',
        {'form': form, 'tracked_complaint': tracked_complaint, 'track_mode': True},
    )


def map_complaint(request):
    """View complaints with coordinates on a map."""
    complaints = Complaint.objects.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    ).values(
        'id', 'complaint_id', 'department', 'status',
        'description', 'latitude', 'longitude'
    )

    complaint_list = list(complaints)
    context = {
        'complaints_json': json.dumps(complaint_list),
        'map_mode': True,
    }
    return render(request, 'complaint.html', context)


@login_required
@role_required(['state_officer', 'district_officer', 'taluka_officer', 'village_officer', 'super_admin'])
def complaint_detail(request, complaint_id):
    """View full complaint details and history."""
    complaint = get_object_or_404(
        Complaint.objects.select_related(),
        complaint_id=complaint_id
    )
    history = complaint.history.all().order_by('-timestamp')

    # Mark as read if not already
    if not complaint.is_read:
        complaint.is_read = True
        complaint.save(update_fields=['is_read'])

    context = {
        'complaint': complaint,
        'history': history,
    }
    return render(request, 'complaint.html', context)


@login_required
@role_required(['state_officer', 'district_officer', 'taluka_officer', 'super_admin'])
def mark_complaint_read(request, complaint_id):
    """Mark complaint as 'In Progress' and log it."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if complaint.status != 'In Progress':
        complaint.status = 'In Progress'
        complaint.save(update_fields=['status'])
        ComplaintHistory.objects.create(
            complaint=complaint,
            status='Marked In Progress',
            updated_by=request.user
        )
        messages.success(request, f'Complaint {complaint_id} marked as In Progress.')
    else:
        messages.info(request, 'Complaint is already In Progress.')
    return redirect('complaint:complaint_detail', complaint_id=complaint_id)


@login_required
@role_required(['state_officer', 'district_officer', 'super_admin'])
def resolve_complaint(request, complaint_id):
    """Resolve a complaint."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if complaint.status != 'Resolved':
        complaint.status = 'Resolved'
        complaint.save(update_fields=['status'])
        ComplaintHistory.objects.create(
            complaint=complaint,
            status='Resolved',
            updated_by=request.user
        )
        messages.success(request, f'Complaint {complaint_id} resolved.')
    else:
        messages.info(request, 'Complaint is already resolved.')
    return redirect('complaint:complaint_detail', complaint_id=complaint_id)


@login_required
@role_required(['state_officer', 'district_officer', 'super_admin'])
def close_complaint(request, complaint_id):
    """Close a complaint (final state)."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if complaint.status != 'Closed':
        complaint.status = 'Closed'
        complaint.save(update_fields=['status'])
        ComplaintHistory.objects.create(
            complaint=complaint,
            status='Closed',
            updated_by=request.user
        )
        messages.success(request, f'Complaint {complaint_id} closed.')
    else:
        messages.info(request, 'Complaint is already closed.')
    return redirect('complaint:complaint_detail', complaint_id=complaint_id)


@login_required
@role_required(['state_officer', 'super_admin'])
def reject_complaint(request, complaint_id):
    """Reject a complaint."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if complaint.status != 'Rejected':
        complaint.status = 'Rejected'
        complaint.save(update_fields=['status'])
        ComplaintHistory.objects.create(
            complaint=complaint,
            status='Rejected',
            updated_by=request.user
        )
        messages.success(request, f'Complaint {complaint_id} rejected.')
    else:
        messages.info(request, 'Complaint is already rejected.')
    return redirect('complaint:complaint_detail', complaint_id=complaint_id)