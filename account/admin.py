from django.contrib import admin
from .models import Citizen, UserProfile


class CitizenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone',
        'district',
        'taluka',
        'village',
        'gender'
    )
    search_fields = ('user__username', 'phone', 'village')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username',)
    list_filter = ('role',)


admin.site.register(Citizen, CitizenAdmin)
admin.site.register(UserProfile, UserProfileAdmin)