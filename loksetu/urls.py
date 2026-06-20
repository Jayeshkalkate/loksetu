from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    # apps
    path('', include('post.urls')),
    path('', include('complaint.urls')),
    path('', include('schemes.urls')),
    path('', include('funds.urls')),
    path('accounts/', include('account.urls')),
    path('api/', include('loksetu.api.urls')), 

    # pages
    path('', views.homepage, name='homepage'),
    path('about/', views.aboutus, name='aboutus'),
    path('services/', views.services, name='services'),
    path('contact/', views.contactus, name='contactus'),
    path('profile/', views.userprofile, name='userprofile'),

    path('departments/', views.departments, name='departments'),
    path('faq/', views.faq, name='faq'),
    path('how_it_works/', views.how_it_works, name='how_it_works'),

    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms_conditions/', views.terms_conditions, name='terms_conditions'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('emergency_contacts/', views.emergency_contacts, name='emergency_contacts'),

    path('post/', views.post, name='post'),
    path('singlepost/', views.singlepost, name='singlepost'),
    
    path('documents/', include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    
