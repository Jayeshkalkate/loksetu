from django.db import connection
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render

from complaints.models import Complaint
from emergency.models import EmergencyContact
from news.models import Announcement
from schemes.models import Scheme


def home(request):
    stats = Complaint.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status__in=['SUBMITTED', 'RECEIVED', 'ASSIGNED'])),
        progress=Count('id', filter=Q(status__in=['UNDER_REVIEW', 'IN_PROGRESS', 'NEEDS_INFO'])),
        resolved=Count('id', filter=Q(status__in=['RESOLVED', 'CLOSED'])))
    return render(request, 'home.html', {
        'stats': stats, 'schemes': Scheme.objects.all()[:3], 'news': Announcement.objects.all()[:3],
        'emergency': EmergencyContact.objects.filter(number__in=['100', '108', '101', '112'])})


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
