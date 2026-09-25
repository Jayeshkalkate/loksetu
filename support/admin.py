from django.contrib import admin

from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'subject', 'user', 'status', 'created')
    list_filter = ('status',)
    search_fields = ('ticket_id', 'subject', 'message', 'user__username')
    readonly_fields = ('ticket_id', 'user', 'subject', 'message', 'created', 'updated')
    fields = ('ticket_id', 'user', 'subject', 'message', 'status', 'response', 'created', 'updated')

    def has_add_permission(self, request):
        return False
