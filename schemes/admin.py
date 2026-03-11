from django.contrib import admin
from .models import Scheme

class SchemeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "scheme_level",
        "state",
        "district",
        "taluka",
        "village",
        "created_at"
    )

    list_filter = ("scheme_level", "district", "taluka", "category")

    search_fields = ("title", "description")

admin.site.register(Scheme, SchemeAdmin)