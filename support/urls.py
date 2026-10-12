from django.urls import path

from . import views

urlpatterns = [
    path('', views.support_form, name='support'),
    path('tickets/', views.support_list, name='support_list'),
    path('tickets/<str:ticket_id>/edit/', views.support_edit, name='support_edit'),
    path('tickets/<str:ticket_id>/delete/', views.support_delete, name='support_delete'),
    path('tickets/<str:ticket_id>/', views.support_detail, name='support_detail'),
]
