from django.urls import path
from . import views

app_name = 'schemes'

urlpatterns = [
    path('', views.schemes, name='schemes'),
    path('<slug:slug>/', views.scheme_detail, name='scheme_detail'),
    path('add/', views.add_scheme, name='add_scheme'),
    path('<slug:slug>/edit/', views.edit_scheme, name='edit_scheme'),
    path('<slug:slug>/delete/', views.delete_scheme, name='delete_scheme'),
    path('<slug:slug>/verify/', views.verify_scheme, name='verify_scheme'),
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
]