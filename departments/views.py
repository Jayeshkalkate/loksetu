from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Department

# "I have a problem, who do I contact?" — maps a citizen need to relevant department categories.
NEED_MAP = [
    ('I am a farmer', ['AGRI']),
    ('I am a student', ['EDU', 'WELFARE']),
    ('I need women & child services', ['WELFARE', 'HEALTH']),
    ('I need housing assistance', ['URBAN']),
    ('I need a driving licence', ['TRANSPORT']),
    ('I have a health concern', ['HEALTH']),
    ('I run a business', ['INDUSTRY']),
    ('I need a certificate or land record', ['ADMIN']),
]


def department_list(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    departments = Department.objects.all()
    if q:
        departments = departments.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(responsibilities__icontains=q))
    if category:
        departments = departments.filter(category=category)

    grouped = {}
    for dep in departments:
        grouped.setdefault(dep.get_category_display(), []).append(dep)

    return render(request, 'departments/list.html', {
        'title': 'Government Departments',
        'query': q,
        'category': category,
        'categories': Department.CATEGORY_CHOICES,
        'grouped': grouped,
        'needs': NEED_MAP,
        'total': departments.count(),
    })


def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'departments/detail.html', {
        'title': department.name,
        'department': department,
        'schemes': department.scheme_set.all(),
        'officers': department.officers.all(),
    })
