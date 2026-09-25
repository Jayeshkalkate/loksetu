from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_approved', 'created')
    list_filter = ('is_approved', 'rating')
    search_fields = ('user__username', 'comment')
    actions = ['approve']

    @admin.action(description='Approve selected reviews')
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
