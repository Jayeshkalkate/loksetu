from django.urls import path

from . import views

urlpatterns = [
    path('', views.fund_list, name='funds'),
]
