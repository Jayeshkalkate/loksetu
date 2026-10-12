import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.throttle import hit, client_ip, throttle
from .forms import ComplaintForm
from .models import CONTENT_TYPES, Complaint, Evidence, Status, StatusHistory


@login_required
@throttle('file', 20, 24 * 3600, per_user=True)
def file_complaint(request):
    form = ComplaintForm(request.POST or None, request.FILES or None,
                         initial={'district': request.user.district_id})
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            c = form.save(commit=False)
            c.citizen = request.user
            c.save()
            if form.cleaned_data.get('evidence'):
                Evidence.objects.create(complaint=c, file=form.cleaned_data['evidence'])
            c.record(request.user, 'Complaint submitted')
        messages.success(request, f'Complaint submitted. Your Complaint ID is {c.complaint_id}. Keep it to track progress.')
        return redirect('complaint_detail', c.complaint_id)
    return render(request, 'complaints/form.html', {'form': form})


@login_required
def edit_complaint(request, cid):
    """Citizens may correct a submitted complaint before a department acts on it."""
    c = get_object_or_404(Complaint, complaint_id=cid, citizen=request.user)
    if c.status != Status.SUBMITTED:
        messages.error(request, 'This complaint can no longer be edited because a department has started processing it.')
        return redirect('complaint_detail', cid)
    form = ComplaintForm(request.POST or None, request.FILES or None, instance=c)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            c = form.save(commit=False)
            c.save()
            if form.cleaned_data.get('evidence'):
                Evidence.objects.create(complaint=c, file=form.cleaned_data['evidence'])
            StatusHistory.objects.create(complaint=c, status=c.status,
                                         note='Complaint details edited by citizen', changed_by=request.user)
            from audit.models import log
            log(request.user, 'Complaint edited', c.complaint_id, new='Citizen updated submitted complaint')
        messages.success(request, 'Your complaint details were updated.')
        return redirect('complaint_detail', c.complaint_id)
    return render(request, 'complaints/form.html', {'form': form, 'complaint': c, 'editing': True})


@login_required
def withdraw_complaint(request, cid):
    """Withdraw instead of hard-deleting so the public-service audit trail remains intact."""
    c = get_object_or_404(Complaint, complaint_id=cid, citizen=request.user)
    if c.status != Status.SUBMITTED:
        messages.error(request, 'Only complaints that have not yet been picked up by a department can be withdrawn.')
        return redirect('complaint_detail', cid)
    if request.method == 'POST':
        c.set_status(Status.WITHDRAWN, request.user, 'Withdrawn by citizen')
        from audit.models import log
        log(request.user, 'Complaint withdrawn', c.complaint_id, old=Status.SUBMITTED, new=Status.WITHDRAWN)
        messages.success(request, f'Complaint {c.complaint_id} was withdrawn. Its history is retained for accountability.')
        return redirect('history')
    return render(request, 'complaints/withdraw.html', {'c': c})


@login_required
def history(request):
    items = Complaint.objects.filter(citizen=request.user).select_related('category')
    return render(request, 'complaints/history.html', {'items': items})


def track(request):
    cid = request.GET.get('id', '').strip().upper()
    if cid:
        # Complaint IDs are sequential, so limit lookups to stop bulk enumeration.
        if not hit(f'track:{client_ip(request)}', 30, 10 * 60):
            messages.error(request, 'Too many lookups. Please wait a few minutes and try again.')
            return render(request, 'complaints/track.html', status=429)
        if Complaint.objects.filter(complaint_id=cid).exists():
            return redirect('complaint_detail', cid)
        messages.error(request, 'No complaint found with that ID. Check the ID and try again.')
    return render(request, 'complaints/track.html')


def detail(request, cid):
    c = get_object_or_404(Complaint.objects.select_related('department', 'category', 'district'), complaint_id=cid)
    owner = c.can_view_private(request.user)
    return render(request, 'complaints/detail.html', {
        'c': c, 'owner': owner, 'evidence': c.evidence.all() if owner else [],
        'history': c.history.all()})


def evidence_file(request, pk):
    """Evidence is private: only the complainant and in-scope staff may open it."""
    e = get_object_or_404(Evidence.objects.select_related('complaint'), pk=pk)
    if not e.complaint.can_view_private(request.user):
        raise Http404  # do not reveal that the file exists
    try:
        fh = e.file.open('rb')
    except (FileNotFoundError, ValueError):
        raise Http404
    ext = os.path.splitext(e.file.name)[1].lower()
    resp = FileResponse(fh, content_type=CONTENT_TYPES.get(ext, 'application/octet-stream'))
    resp['Content-Disposition'] = f'inline; filename="{e.complaint.complaint_id}-{e.pk}{ext}"'
    resp['X-Content-Type-Options'] = 'nosniff'
    resp['Content-Security-Policy'] = "default-src 'none'; sandbox"
    resp['Cache-Control'] = 'private, no-store'
    return resp


def complaint_map(request):
    return render(request, 'complaints/map.html')


def map_data(request):
    # Public-safe: no titles, descriptions or citizen data; coordinates rounded to ~1 km.
    data = cache.get('map_data')
    if data is None:
        qs = (Complaint.objects.exclude(latitude=None).exclude(longitude=None).exclude(status=Status.WITHDRAWN)
              .select_related('category').order_by('-created')[:2000])
        pts = [{'lat': round(c.latitude, 2), 'lng': round(c.longitude, 2),
                'status': c.get_status_display(), 'category': c.category.name} for c in qs]
        districts = list(Complaint.objects.exclude(status=Status.WITHDRAWN).values('district__name', 'status').annotate(n=Count('id')))
        data = {'points': pts, 'districts': districts}
        cache.set('map_data', data, 60)
    return JsonResponse(data)
