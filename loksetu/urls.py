from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from post import views as post_views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # App URLs (namespaced)
    path("accounts/", include("account.urls")),
    path("complaints/", include("complaint.urls")),
    path("schemes/", include("schemes.urls")),
    path("funds/", include("funds.urls")),
    path("documents/", include("documents.urls")),
    path("posts/", include("post.urls")),          # namespaced (post:post_list / post:post_detail)

    # API (if any)
    path("api/", include("loksetu.api.urls")),

    # Public pages
    path("", views.homepage, name="homepage"),
    path("about/", views.aboutus, name="aboutus"),
    path("services/", views.services, name="services"),
    path("contact/", views.contactus, name="contactus"),
    path("profile/", views.userprofile, name="userprofile"),
    path("departments/", views.departments, name="departments"),
    path("faq/", views.faq, name="faq"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-conditions/", views.terms_conditions, name="terms_conditions"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("emergency-contacts/", views.emergency_contacts, name="emergency_contacts"),

    # News / announcements feed — the site-wide nav (base.html/header.html)
    # links here with the unnamespaced names 'news' / 'news_detail'.
    # These were previously undefined, which threw NoReverseMatch on every
    # page that includes the nav (i.e. almost the whole site).
    path("news/", post_views.post_list, name="news"),
    path("news/<int:pk>/", post_views.post_detail, name="news_detail"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)