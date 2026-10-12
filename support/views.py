from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.throttle import throttle
from .forms import SupportTicketForm
from .models import SupportTicket


@login_required
@throttle('support', 10, 24 * 3600, per_user=True)
def support_form(request):
    form = SupportTicketForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()
        messages.success(request, f'Your ticket {ticket.ticket_id} was submitted. We will get back to you soon.')
        return redirect('support_list')
    tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, 'support/form.html', {'form': form, 'tickets': tickets})


@login_required
def support_list(request):
    tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, 'support/list.html', {'title': 'My support tickets', 'tickets': tickets})


@login_required
def support_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, user=request.user)
    return render(request, 'support/detail.html', {'ticket': ticket})


@login_required
def support_edit(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, user=request.user)
    if ticket.status != SupportTicket.Status.OPEN:
        messages.error(request, 'Only open tickets can be edited.')
        return redirect('support_detail', ticket_id)
    form = SupportTicketForm(request.POST or None, instance=ticket)
    if request.method == 'POST' and form.is_valid():
        form.save()
        from audit.models import log
        log(request.user, 'Support ticket edited', ticket.ticket_id, new='Citizen updated open ticket')
        messages.success(request, f'Ticket {ticket.ticket_id} was updated.')
        return redirect('support_detail', ticket.ticket_id)
    return render(request, 'support/form.html', {'form': form, 'tickets': [ticket], 'editing': True, 'ticket': ticket})


@login_required
def support_delete(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, user=request.user)
    if ticket.status != SupportTicket.Status.OPEN:
        messages.error(request, 'Only open tickets can be deleted. Please contact support for an active case.')
        return redirect('support_detail', ticket_id)
    if request.method == 'POST':
        ticket_id_label = ticket.ticket_id
        from audit.models import log
        log(request.user, 'Support ticket deleted', ticket_id_label, old=ticket.subject, new='Deleted by owner')
        ticket.delete()
        messages.success(request, f'Ticket {ticket_id_label} was deleted.')
        return redirect('support_list')
    return render(request, 'support/delete.html', {'ticket': ticket})
