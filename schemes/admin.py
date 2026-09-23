from django.contrib import admin
from .models import Scheme


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'category', 'is_verified', 'created_at')
    search_fields = ('title', 'description', 'slug')
    list_filter = ('level', 'category', 'is_verified', 'state')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'eligibility', 'benefits')}),
        ('Classification', {'fields': ('category', 'level')}),
        ('Location', {'fields': ('state', 'district', 'taluka', 'village')}),
        ('Media & Links', {'fields': ('image', 'official_link')}),
        ('Metadata', {'fields': ('created_by', 'is_verified', 'created_at', 'updated_at')}),
    )
    actions = ['mark_verified', 'mark_unverified']

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} schemes marked as verified.")
    mark_verified.short_description = "Mark selected schemes as verified"

    def mark_unverified(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"{queryset.count()} schemes marked as unverified.")
    mark_unverified.short_description = "Mark selected schemes as unverified"