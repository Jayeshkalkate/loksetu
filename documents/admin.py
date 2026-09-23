from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'is_public', 'get_file_size')
    list_filter = ('is_public', 'uploaded_at', 'uploaded_by')
    search_fields = ('title', 'uploaded_by__username', 'uploaded_by__email')
    readonly_fields = ('uploaded_at', 'updated_at')
    ordering = ('-uploaded_at',)
    fieldsets = (
        (None, {'fields': ('title', 'file', 'is_public')}),
        ('Metadata', {'fields': ('uploaded_by', 'uploaded_at', 'updated_at')}),
    )
    actions = ['make_public', 'make_private']

    def make_public(self, request, queryset):
        queryset.update(is_public=True)
        self.message_user(request, 'Selected documents are now public.')
    make_public.short_description = 'Mark selected as public'

    def make_private(self, request, queryset):
        queryset.update(is_public=False)
        self.message_user(request, 'Selected documents are now private.')
    make_private.short_description = 'Mark selected as private'