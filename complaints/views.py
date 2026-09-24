from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ComplaintForm
from .models import Complaint, Evidence, Status


@login_required
def file_complaint(request):
    form = ComplaintForm(request.POST or None, request.FILES or None,
                         initial={'district': request.user.district_id})
    if request.method == 'POST' and form.is_valid():
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
def history(request):
    return render(request, 'complaints/history.html', {'items': Complaint.objects.filter(citizen=request.user)})


def track(request):
    cid = request.GET.get('id', '').strip().upper()
    if cid:
        if Complaint.objects.filter(complaint_id=cid).exists():
            return redirect('complaint_detail', cid)
        messages.error(request, 'No complaint found with that ID. Check the ID and try again.')
    return render(request, 'complaints/track.html')


def detail(request, cid):
    c = get_object_or_404(Complaint.objects.select_related('department', 'category', 'district'), complaint_id=cid)
    owner = request.user.is_authenticated and (request.user == c.citizen or request.user.is_staff)
    return render(request, 'complaints/detail.html', {'c': c, 'owner': owner})


def complaint_map(request):
    return render(request, 'complaints/map.html')


def map_data(request):
    # Public-safe: no titles, descriptions or citizen data; coordinates rounded to ~1 km.
    pts = [{'lat': round(c.latitude, 2), 'lng': round(c.longitude, 2),
            'status': c.get_status_display(), 'category': c.category.name}
           for c in Complaint.objects.exclude(latitude=None).exclude(longitude=None).select_related('category')]
    districts = list(Complaint.objects.values('district__name', 'status').annotate(n=Count('id')))
    return JsonResponse({'points': pts, 'districts': districts})
