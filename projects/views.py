from django.shortcuts import get_object_or_404, render

from .models import Project


def project_list(request):
    status = request.GET.get('status', '').strip()
    projects = Project.objects.select_related('department', 'district').all()
    if status:
        projects = projects.filter(status=status)
    return render(request, 'projects/list.html', {
        'title': 'Government Projects',
        'projects': projects,
        'status': status,
        'statuses': Project.Status.choices,
        'total': projects.count(),
    })


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related('department', 'district'), pk=pk)
    return render(request, 'projects/detail.html', {'title': project.name, 'project': project})
