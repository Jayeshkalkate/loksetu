from django.urls import path

from . import views

urlpatterns = [
    path('', views.appointment_form, name='appointment'),
    path('my/', views.appointment_list, name='appointment_list'),
    path('my/<str:appointment_id>/', views.appointment_detail, name='appointment_detail'),
]
