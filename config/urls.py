from django.contrib import admin
from django.urls import include, path
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from core.views import about, healthz, home, robots
from emergency.models import EmergencyContact
from news.models import Announcement
from schemes.models import Scheme
from jobs.models import JobNotification

admin.site.site_header = 'LOKSETU administration'
admin.site.site_title = 'LOKSETU admin'


def page(title, body):
    return TemplateView.as_view(template_name='page.html', extra_context={'title': title, 'body': body})


class PublicListingView(ListView):
    """Generic public listing that never exposes scheduled future-dated content."""
    template_name = 'list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        field_names = {field.name for field in self.model._meta.get_fields() if getattr(field, 'concrete', False)}
        if 'published' in field_names:
            qs = qs.filter(published__lte=timezone.now())
        return qs


def listing(model, title):
    return PublicListingView.as_view(model=model, extra_context={'title': title})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', healthz, name='healthz'),
    path('robots.txt', robots),
    path('', home, name='home'),
    path('', include('accounts.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('complaints/', include('complaints.urls')),
    path('schemes/', listing(Scheme, 'Government Schemes'), name='schemes'),
    path('departments/', include('departments.urls')),
    path('news/', listing(Announcement, 'News & Announcements'), name='news'),
    path('jobs/', listing(JobNotification, 'Job & Recruitment Notifications'), name='jobs'),
    path('gallery/', include('gallery.urls')),
    path('reviews/', include('reviews.urls')),
    path('appointment/', include('appointments.urls')),
    path('emergency/', listing(EmergencyContact, 'Emergency Contacts'), name='emergency'),
    path('projects/', include('projects.urls')),
    path('funds/', include('funds.urls')),
    path('documents/', include('documents.urls')),
    path('reports/', include('reports.urls')),
    path('faq/', include('faq.urls')),
    path('support/', include('support.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('about/', about, name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('privacy/', page('Privacy Policy', 'LOKSETU uses account and contact details to authenticate users, manage complaints and appointments, and respond to support tickets. Complaint descriptions and evidence are restricted to the citizen and authorized staff handling the case. The public issue map shows approximate locations and issue categories, not names, complaint titles, descriptions, or contact details. Reviews are published only after moderation. Do not upload sensitive personal information unless it is necessary to explain the issue. Configure production storage, retention, and access controls before accepting real citizen data.'), name='privacy'),
    path('terms/', page('Terms & Conditions', 'Submit truthful complaints and provide only information needed to resolve the issue. You may edit or withdraw a complaint while it is still in Submitted status; withdrawals remain in the audit history instead of being physically erased. You may reschedule or cancel pending appointments and delete open support tickets or your own reviews. Do not upload unlawful, abusive, or unrelated content. LOKSETU is an independent project and cannot guarantee that a public authority or service provider will act unless an authorized integration confirms receipt.'), name='terms'),
    path('disclaimer/', page('Disclaimer', 'LOKSETU is an independent project and is not an official Government of Maharashtra website unless stated. Always verify scheme details with the official source shown.'), name='disclaimer'),
]
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
