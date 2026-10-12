from django.urls import path

from . import views

urlpatterns = [
    path('', views.review_list, name='reviews'),
    path('<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('<int:pk>/delete/', views.review_delete, name='review_delete'),
]
