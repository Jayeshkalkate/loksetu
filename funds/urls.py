from django.urls import path
from . import views

app_name = 'funds'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Fund CRUD
    path('fund/create/', views.fund_create, name='fund_create'),
    path('fund/<int:pk>/edit/', views.fund_edit, name='fund_edit'),
    path('fund/<int:pk>/delete/', views.fund_delete, name='fund_delete'),
    path('fund/<int:pk>/json/', views.fund_detail_json, name='fund_detail_json'),

    # Project CRUD (create can optionally take fund_pk)
    path('project/create/', views.project_create, name='project_create'),
    path('project/create/<int:fund_pk>/', views.project_create, name='project_create_with_fund'),
    path('project/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete'),

    # Location CRUD
    path('location/create/', views.location_create, name='location_create'),
    path('location/<int:pk>/edit/', views.location_edit, name='location_edit'),
    path('location/<int:pk>/delete/', views.location_delete, name='location_delete'),

    # Bulk upload
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
]