from django.contrib import admin
from .models import Citizen, UserProfile


@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "district", "taluka", "village", "gender", "masked_aadhaar")
    # NOTE: aadhaar is encrypted at rest, so it can't be searched with SQL
    # LIKE — do not add it back to search_fields.
    search_fields = ("user__username", "user__first_name", "phone")
    list_filter = ("district", "taluka", "gender")
    raw_id_fields = ("user",)
    readonly_fields = ("masked_aadhaar",)
    ordering = ("-id",)

    @admin.display(description="Aadhaar")
    def masked_aadhaar(self, obj):
        return obj.masked_aadhaar


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_district", "assigned_taluka", "assigned_village")
    search_fields = ("user__username", "user__first_name")
    list_filter = ("role", "assigned_district")
    raw_id_fields = ("user",)
    ordering = ("-id",)