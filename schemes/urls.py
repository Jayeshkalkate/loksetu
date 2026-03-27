from django.urls import path
from . import views

urlpatterns = [
    path('schemes/', views.schemes, name='schemes'),
    path('schemes/<slug:slug>/', views.scheme_detail, name='scheme_detail'),
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('add-scheme/', views.add_scheme, name='add_scheme'),
]