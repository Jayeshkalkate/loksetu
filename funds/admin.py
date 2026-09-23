from django.contrib import admin
from .models import Fund, Project, Location, Proof, Complaint


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    fields = ('name', 'sanctioned_amount', 'used_amount', 'status', 'start_date', 'end_date')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'total_amount', 'released_amount', 'used_amount', 'year', 'location')
    search_fields = ('title', 'department')
    list_filter = ('year', 'location', 'department')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProjectInline]
    fieldsets = (
        (None, {'fields': ('title', 'department', 'year', 'location')}),
        ('Amounts', {'fields': ('total_amount', 'released_amount')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def used_amount(self, obj):
        return obj.used_amount
    used_amount.short_description = 'Used Amount'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund', 'sanctioned_amount', 'used_amount', 'progress_percentage', 'status', 'start_date')
    list_filter = ('status', 'fund__year')
    search_fields = ('name', 'fund__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('fund', 'name', 'status', 'start_date', 'end_date')}),
        ('Amounts', {'fields': ('sanctioned_amount', 'used_amount')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'parent')
    list_filter = ('type',)
    search_fields = ('name',)


@admin.register(Proof)
class ProofAdmin(admin.ModelAdmin):
    list_display = ('project', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('project__name',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('project', 'user_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user_name', 'description')