from django.contrib import admin
from .models import complaint


class complaintAdmin(admin.ModelAdmin):

    list_display = (
        "complaint_id",
        "title",
        "department",
        "district",
        "status",
        "created_at"
    )

    list_filter = (
        "status",
        "department",
        "district"
    )

    search_fields = (
        "title",
        "description",
        "full_name",
        "phone"
    )


admin.site.register(complaint, complaintAdmin)

