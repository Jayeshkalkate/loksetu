from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'category', 'published')
    list_filter = ('category', 'department')
    search_fields = ('title', 'description')
