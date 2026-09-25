from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.utils import timezone

from complaints.models import Complaint, Status
from documents.models import Document
from faq.models import FAQ
from funds.models import Fund
from news.models import Announcement
from projects.models import Project
from reports.models import Report
from schemes.models import Scheme
from support.models import SupportTicket


@login_required
def dashboard(request):
    """Send citizens to their existing 'My dashboard' page; staff get the analytics view."""
    if request.user.is_staff:
        return staff_dashboard(request)
    return redirect('profile')


@staff_member_required(login_url='login')
def staff_dashboard(request):
    user = request.user
    qs = Complaint.objects.all()
    scoped = False
    if not user.is_superuser and user.role == 'DEPT_ADMIN':
        qs = qs.filter(department_id=user.department_id)
        scoped = True
    elif not user.is_superuser and user.role == 'OFFICER':
        qs = qs.filter(assigned_to=user)
        scoped = True

    status_counts = {r['status']: r['n'] for r in qs.values('status').annotate(n=Count('id'))}
    status_labels = [label for _, label in Status.choices]
    status_values = [status_counts.get(code, 0) for code, _ in Status.choices]

    dept_rows = list(qs.exclude(department=None).values('department__name')
                     .annotate(n=Count('id')).order_by('-n')[:8])
    district_rows = list(qs.exclude(district=None).values('district__name')
                         .annotate(n=Count('id')).order_by('-n')[:10])
    category_rows = list(qs.values('category__name').annotate(n=Count('id')).order_by('-n')[:8])

    since = (timezone.localdate() - timedelta(days=29))
    trend_qs = (qs.filter(created__date__gte=since)
               .annotate(day=TruncDate('created')).values('day')
               .annotate(n=Count('id')).order_by('day'))
    trend_map = {row['day'].isoformat(): row['n'] for row in trend_qs}
    trend_labels = [(since + timedelta(days=i)).isoformat() for i in range(30)]
    trend_values = [trend_map.get(d, 0) for d in trend_labels]

    resolved_qs = qs.filter(status__in=[Status.RESOLVED, Status.CLOSED])
    duration = ExpressionWrapper(F('updated') - F('created'), output_field=DurationField())
    avg_duration = resolved_qs.annotate(duration=duration).aggregate(avg=Avg('duration'))['avg']
    avg_resolution_days = round(avg_duration.total_seconds() / 86400, 1) if avg_duration else None

    total = qs.count()
    resolved_count = resolved_qs.count()
    resolution_rate = round(resolved_count / total * 100, 1) if total else 0

    site_counts = None
    if user.is_superuser or user.role == 'SUPER':
        site_counts = [
            ('Schemes', Scheme.objects.count()),
            ('News', Announcement.objects.count()),
            ('Projects', Project.objects.count()),
            ('Funds', Fund.objects.count()),
            ('Documents', Document.objects.count()),
            ('Reports', Report.objects.count()),
            ('FAQs', FAQ.objects.count()),
            ('Open tickets', SupportTicket.objects.exclude(
                status__in=[SupportTicket.Status.RESOLVED, SupportTicket.Status.CLOSED]).count()),
        ]

    return render(request, 'dashboard/staff.html', {
        'title': 'Dashboard',
        'scoped': scoped,
        'total': total,
        'resolution_rate': resolution_rate,
        'avg_resolution_days': avg_resolution_days,
        'status_labels': status_labels,
        'status_values': status_values,
        'dept_labels': [r['department__name'] for r in dept_rows],
        'dept_values': [r['n'] for r in dept_rows],
        'district_labels': [r['district__name'] for r in district_rows],
        'district_values': [r['n'] for r in district_rows],
        'category_labels': [r['category__name'] for r in category_rows],
        'category_values': [r['n'] for r in category_rows],
        'trend_labels': trend_labels,
        'trend_values': trend_values,
        'site_counts': site_counts,
    })
