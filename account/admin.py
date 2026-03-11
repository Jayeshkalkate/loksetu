from django.contrib import admin
from .models import Citizen
from .models import UserProfile


class CitizenAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'ward', 'pincode')
    search_fields = ('user__username', 'phone', 'village')

admin.site.register(Citizen, CitizenAdmin)
admin.site.register(UserProfile)