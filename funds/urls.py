from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('create/', views.create_fund, name='create_fund'),
    path('edit/<int:id>/', views.edit_fund, name='edit_fund'),
    path('delete/<int:id>/', views.delete_fund, name='delete_fund'),

    path('funds-bulk-upload/', views.funds_bulk_upload, name='funds_bulk_upload'),
]