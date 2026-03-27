from django.urls import path
from .views import dashboard, fund_detail, project_detail, location_detail
from . import views

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('fund/<int:fund_id>/', fund_detail, name='fund_detail'),
    path('project/<int:project_id>/', project_detail, name='project_detail'),
    path('location/<int:location_id>/', location_detail, name='location_detail'),
    path('funds-bulk-upload/', views.funds_bulk_upload, name='funds_bulk_upload'),
]