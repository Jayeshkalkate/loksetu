from django.contrib import admin
from .models import Citizen

class CitizenAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'village', 'ward', 'pincode')
    search_fields = ('user__username', 'phone', 'village')

admin.site.register(Citizen, CitizenAdmin)
