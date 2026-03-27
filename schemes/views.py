from django.shortcuts import render, get_object_or_404, redirect
from .models import Scheme
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import BulkUploadForm
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from .forms import SchemeForm

@login_required
def add_scheme(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if request.method == 'POST':
        form = SchemeForm(request.POST, request.FILES)
        if form.is_valid():
            scheme = form.save(commit=False)
            scheme.created_by = request.user
            scheme.save()
            messages.success(request, "Scheme added successfully!")
            return redirect('schemes')
    else:
        form = SchemeForm()

    return render(request, 'add_scheme.html', {'form': form})

@login_required
def bulk_upload(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']

            try:
                data = json.load(file)
            except Exception:
                return HttpResponse("Invalid JSON")

            for item in data:
                if not item.get('title'):
                    continue

                if not Scheme.objects.filter(title=item.get('title')).exists():
                    Scheme.objects.create(
    title=item.get('title'),
    description=item.get('description'),
    eligibility=item.get('eligibility'),
    benefits=item.get('benefits'),
    category=item.get('category'),
    level=item.get('level'),
    state=item.get('state', 'Maharashtra'),
    district=item.get('district'),
    taluka=item.get('taluka'),
    village=item.get('village'),
    official_link=item.get('official_link'),
    created_by=request.user
)
                    
            messages.success(request, "Schemes uploaded successfully!")
            return redirect('schemes')

    else:
        form = BulkUploadForm()

    return render(request, 'bulk_upload.html', {'form': form})

@login_required
def schemes(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')

    qs = Scheme.objects.all().order_by('-created_at')
    
    # ✅ ADD THIS
    if request.user.is_authenticated and not request.user.is_superuser:
        qs = qs.filter(state="Maharashtra")
    
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    if category:
        qs = qs.filter(category=category)

    # ✅ Split data
    central = qs.filter(level='central')
    state = qs.filter(level='state')
    district = qs.filter(level='district')
    taluka = qs.filter(level='taluka')
    village = qs.filter(level='village')

    # ✅ Pagination (simple)
    central = Paginator(central, 6).get_page(request.GET.get('central_page'))
    state = Paginator(state, 6).get_page(request.GET.get('state_page'))
    district = Paginator(district, 6).get_page(request.GET.get('district_page'))
    taluka = Paginator(taluka, 6).get_page(request.GET.get('taluka_page'))
    village = Paginator(village, 6).get_page(request.GET.get('village_page'))

    return render(request, 'schemes.html', {
        'schemes': {
            'central': central,
            'state': state,
            'district': district,
            'taluka': taluka,
            'village': village
        },
        'search_query': search,
        'category': category,
        'total_count': qs.count(),
        'user_state': "Maharashtra"
    })


@login_required
def scheme_detail(request, slug):
    scheme = get_object_or_404(Scheme, slug=slug)
    return render(request, 'scheme_detail.html', {'scheme': scheme})