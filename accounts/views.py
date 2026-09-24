from django.contrib import messages
from django.contrib.auth import login, views as auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from core.throttle import throttle
from .forms import RegisterForm

login_view = throttle('login', 20, 15 * 60)(auth.LoginView.as_view(redirect_authenticated_user=True))
password_reset_view = throttle('pwreset', 5, 60 * 60)(auth.PasswordResetView.as_view())


@throttle('register', 10, 60 * 60)
def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())  # role defaults to CITIZEN; staff roles are set only by admins
        messages.success(request, 'Account created. Welcome to LOKSETU.')
        return redirect('profile')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    counts = {r['status']: r['n'] for r in
              request.user.complaint_set.values('status').annotate(n=Count('id'))}
    stats = {
        'total': sum(counts.values()),
        'pending': counts.get('SUBMITTED', 0) + counts.get('RECEIVED', 0) + counts.get('ASSIGNED', 0),
        'progress': counts.get('UNDER_REVIEW', 0) + counts.get('IN_PROGRESS', 0) + counts.get('NEEDS_INFO', 0),
        'resolved': counts.get('RESOLVED', 0),
        'closed': counts.get('CLOSED', 0),
    }
    notifications = list(request.user.notification_set.all()[:10])
    response = render(request, 'profile.html', {'stats': stats, 'notifications': notifications})
    request.user.notification_set.filter(pk__in=[n.pk for n in notifications], is_read=False).update(is_read=True)
    return response
