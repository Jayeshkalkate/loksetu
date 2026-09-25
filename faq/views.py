from itertools import groupby

from django.shortcuts import render

from .models import FAQ


def faq_list(request):
    faqs = FAQ.objects.all()
    grouped = [(cat, list(items)) for cat, items in groupby(faqs, key=lambda f: f.category)]
    return render(request, 'faq/list.html', {'title': 'Frequently Asked Questions', 'grouped': grouped})
