from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render

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
    stats = Complaint.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status__in=['SUBMITTED', 'RECEIVED', 'ASSIGNED'])),
        progress=Count('id', filter=Q(status__in=['UNDER_REVIEW', 'IN_PROGRESS', 'NEEDS_INFO'])),
        resolved=Count('id', filter=Q(status__in=['RESOLVED', 'CLOSED'])))
    return render(request, 'home.html', {
        'stats': stats, 'schemes': Scheme.objects.all()[:3], 'news': Announcement.objects.all()[:3],
        'emergency': EmergencyContact.objects.filter(number__in=['100', '108', '101', '112'])})


def about(request):
    return render(request, 'about.html', {
        'title': 'About',
        'facts': MAHARASHTRA_FACTS,
        'districts': District.objects.all()[:12],
        'district_count': District.objects.count(),
    })


def healthz(request):
    """Liveness/readiness probe for the host: confirms the app can reach its database."""
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
    except Exception:
        return HttpResponse('db error', status=503, content_type='text/plain')
    return HttpResponse('ok', content_type='text/plain')


def robots(request):
    return HttpResponse('User-agent: *\nDisallow: /admin/\nDisallow: /complaints/evidence/\n',
                        content_type='text/plain')


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)
