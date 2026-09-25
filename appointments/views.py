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
