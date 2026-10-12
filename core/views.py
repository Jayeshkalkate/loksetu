from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from complaints.models import Complaint
from departments.models import District
from emergency.models import EmergencyContact
from news.models import Announcement
from schemes.models import Scheme

# Administrative facts about Maharashtra shown on the About page. These are stable
# geography/administration figures, each with its reference year and source — not
# app data — so they live here as a constant rather than in the database.
MAHARASHTRA_FACTS = {
    'districts': {'value': 36, 'label': 'Districts'},
    'divisions': {'value': 6, 'label': 'Revenue divisions'},
    'talukas': {'value': 355, 'label': 'Talukas'},
    'villages': {'value': '43,665', 'label': 'Villages', 'year': 2022},
    'cities': {'value': 534, 'label': 'Cities / urban agglomerations'},
    'area': {'value': '~3,08,000 km²', 'label': 'Geographical area'},
    'coastline': {'value': '720 km', 'label': 'Coastline'},
    'population': {'value': '11.24 crore', 'label': 'Population', 'year': 2011, 'source': 'Census 2011'},
}


def home(request):
    stats = Complaint.objects.exclude(status='WITHDRAWN').aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status__in=['SUBMITTED', 'RECEIVED', 'ASSIGNED'])),
        progress=Count('id', filter=Q(status__in=['UNDER_REVIEW', 'IN_PROGRESS', 'NEEDS_INFO'])),
        resolved=Count('id', filter=Q(status__in=['RESOLVED', 'CLOSED'])))
    return render(request, 'home.html', {
        'stats': stats,
        'schemes': Scheme.objects.filter(published__lte=timezone.now()).order_by('-published')[:3],
        'news': Announcement.objects.filter(published__lte=timezone.now()).order_by('-published')[:3],
        'emergency': EmergencyContact.objects.filter(number__in=['100', '108', '101', '112'])})


def about(request):
    return render(request, 'about.html', {
        'title': 'About',
        'facts': MAHARASHTRA_FACTS,
        'districts': District.objects.all()[:12],
        'district_count': District.objects.count(),
    })


def healthz(request):
    """Cross-origin-safe liveness/readiness probe for Render and the static loader.

    This endpoint exposes no user data and accepts only a read-only database probe, so
    wildcard CORS is safe here. The loader needs to read the status/body from a separate
    Render Static Site origin; without these headers the browser would block that check.
    """
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
    except Exception:
        response = HttpResponse('db error', status=503, content_type='text/plain')
    else:
        response = HttpResponse('ok', content_type='text/plain')

    response['Access-Control-Allow-Origin'] = '*'
    response['Cache-Control'] = 'no-store, max-age=0'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


def robots(request):
    return HttpResponse('User-agent: *\nDisallow: /admin/\nDisallow: /complaints/evidence/\n',
                        content_type='text/plain')


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)
