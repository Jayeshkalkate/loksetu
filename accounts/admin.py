from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class LoksetuUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('LOKSETU', {'fields': ('role', 'mobile', 'district', 'department')}),)
    list_display = ('username', 'email', 'role', 'department', 'is_staff')
    list_filter = UserAdmin.list_filter + ('role',)
