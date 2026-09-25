from django.contrib import admin
from django.urls import include, path
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


def listing(model, title):
    return ListView.as_view(model=model, template_name='list.html', paginate_by=20,
                            extra_context={'title': title})


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
    path('privacy/', page('Privacy Policy', 'We collect only the details needed to process your complaints. Your contact details and complaint description are never shown publicly.'), name='privacy'),
    path('terms/', page('Terms & Conditions', 'Submit only genuine complaints. False or abusive reports may lead to account suspension.'), name='terms'),
    path('disclaimer/', page('Disclaimer', 'LOKSETU is an independent project and is not an official Government of Maharashtra website unless stated. Always verify scheme details with the official source shown.'), name='disclaimer'),
]
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
