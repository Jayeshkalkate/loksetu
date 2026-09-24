from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import ListView, TemplateView
from core.views import home
from departments.models import Department
from emergency.models import EmergencyContact
from news.models import Announcement
from schemes.models import Scheme


def page(title, body):
    return TemplateView.as_view(template_name='page.html', extra_context={'title': title, 'body': body})


def listing(model, title):
    return ListView.as_view(model=model, template_name='list.html', extra_context={'title': title})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('accounts.urls')),
    path('complaints/', include('complaints.urls')),
    path('schemes/', listing(Scheme, 'Government Schemes'), name='schemes'),
    path('departments/', listing(Department, 'Departments'), name='departments'),
    path('news/', listing(Announcement, 'News & Announcements'), name='news'),
    path('emergency/', listing(EmergencyContact, 'Emergency Contacts'), name='emergency'),
    path('about/', page('About', 'LOKSETU is a bridge between the citizens of Maharashtra and their government: report civic issues, track them, and find schemes, news and public projects in one place.'), name='about'),
    path('contact/', page('Contact', 'Write to support@example.com. For emergencies, use the Emergency Contacts page.'), name='contact'),
    path('privacy/', page('Privacy Policy', 'We collect only the details needed to process your complaints. Your contact details and complaint description are never shown publicly.'), name='privacy'),
    path('terms/', page('Terms & Conditions', 'Submit only genuine complaints. False or abusive reports may lead to account suspension.'), name='terms'),
    path('disclaimer/', page('Disclaimer', 'LOKSETU is an independent project and is not an official Government of Maharashtra website unless stated. Always verify scheme details with the official source shown.'), name='disclaimer'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
