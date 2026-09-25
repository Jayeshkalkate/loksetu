from django.shortcuts import render

from .models import Report


def report_list(request):
    report_type = request.GET.get('type', '').strip()
    reports = Report.objects.select_related('department').all()
    if report_type:
        reports = reports.filter(report_type=report_type)
    return render(request, 'reports/list.html', {
        'title': 'Reports & Publications',
        'reports': reports,
        'report_type': report_type,
        'types': Report.ReportType.choices,
        'total': reports.count(),
    })
