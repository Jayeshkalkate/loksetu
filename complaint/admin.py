from django.contrib import admin
from .models import Complaint, ComplaintHistory

admin.site.register(ComplaintHistory)

class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        "complaint_id",
        "title",
        "department",
        "district",
        "status",
        "is_read",
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

admin.site.register(Complaint, ComplaintAdmin)