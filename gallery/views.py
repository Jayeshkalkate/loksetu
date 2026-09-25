from itertools import groupby

from django.shortcuts import render

from .models import GalleryImage


def gallery_list(request):
    images = GalleryImage.objects.order_by('category', '-uploaded')
    grouped = [(cat, list(items)) for cat, items in groupby(images, key=lambda i: i.get_category_display())]
    return render(request, 'gallery/list.html', {'title': 'Gallery', 'grouped': grouped})
