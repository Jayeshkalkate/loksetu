"""
URL configuration for loksetu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    # POST OR NEWS URL
    path('', include('post.urls')),

    # Complaint URL
    path('', include('complaint.urls')),
    
    # Schemes URL
    path('', include('schemes.urls')),

    path('', views.homepage, name='homepage'),
    path('about/', views.aboutus, name='aboutus'),
    path('services/', views.services, name='services'),
    path('contact/', views.contactus, name='contactus'),
    path('profile/', views.userprofile, name='userprofile'),

    path('departments/', views.departments, name='departments'),
    path('village-info/', views.village_info, name='village_info'),

    path('post/', views.post, name='post'),
    path('singlepost/', views.singlepost, name='singlepost'),

    # accounts app
    path('accounts/', include('account.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)