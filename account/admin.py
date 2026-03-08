from django.contrib import admin
from .models import Citizen
from .models import State, District, Taluka, Village, UserProfile


class CitizenAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'village', 'ward', 'pincode')
    search_fields = ('user__username', 'phone', 'village')

admin.site.register(Citizen, CitizenAdmin)
admin.site.register(State)
admin.site.register(District)
admin.site.register(Taluka)
admin.site.register(Village)
admin.site.register(UserProfile)