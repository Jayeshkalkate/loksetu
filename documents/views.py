from django.shortcuts import render

from .models import Document


def document_list(request):
    category = request.GET.get('category', '').strip()
    documents = Document.objects.select_related('department').all()
    if category:
        documents = documents.filter(category=category)
    return render(request, 'documents/list.html', {
        'title': 'Official Documents',
        'documents': documents,
        'category': category,
        'categories': Document.Category.choices,
        'total': documents.count(),
    })
