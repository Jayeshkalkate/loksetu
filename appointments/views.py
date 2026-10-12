from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.throttle import throttle
from .forms import AppointmentForm
from .models import Appointment


@login_required
@throttle('appointment', 10, 24 * 3600, per_user=True)
def appointment_form(request):
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.user = request.user
        appointment.save()
        messages.success(request, f'Appointment {appointment.appointment_id} requested. '
                                   f'We will confirm it shortly.')
        return redirect('appointment_list')
    appointments = Appointment.objects.filter(user=request.user).select_related('department')
    return render(request, 'appointments/form.html', {'form': form, 'appointments': appointments})


@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user).select_related('department')
    return render(request, 'appointments/list.html', {'title': 'My appointments', 'appointments': appointments})


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, user=request.user)
    return render(request, 'appointments/detail.html', {'appointment': appointment})


@login_required
def appointment_edit(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, user=request.user)
    if appointment.status != Appointment.Status.PENDING:
        messages.error(request, 'Only pending appointments can be rescheduled.')
        return redirect('appointment_detail', appointment_id)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        from audit.models import log
        log(request.user, 'Appointment rescheduled', appointment.appointment_id,
            new=f'{appointment.preferred_date} {appointment.preferred_time}')
        messages.success(request, f'Appointment {appointment.appointment_id} was updated.')
        return redirect('appointment_detail', appointment.appointment_id)
    return render(request, 'appointments/form.html', {
        'form': form, 'appointments': [appointment], 'editing': True, 'appointment_obj': appointment,
    })


@login_required
def appointment_cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, user=request.user)
    if appointment.status != Appointment.Status.PENDING:
        messages.error(request, 'Only pending appointments can be cancelled. Please contact support if you need help.')
        return redirect('appointment_detail', appointment_id)
    if request.method == 'POST':
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status', 'updated'])
        from audit.models import log
        log(request.user, 'Appointment cancelled', appointment.appointment_id,
            old=Appointment.Status.PENDING, new=Appointment.Status.CANCELLED)
        messages.success(request, f'Appointment {appointment.appointment_id} was cancelled.')
        return redirect('appointment_list')
    return render(request, 'appointments/cancel.html', {'appointment': appointment})
