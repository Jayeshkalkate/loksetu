from django.contrib import admin
from .models import Scheme

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'category', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('level', 'category')
    prepopulated_fields = {'slug': ('title',)}