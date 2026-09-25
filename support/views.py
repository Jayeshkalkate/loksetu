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
