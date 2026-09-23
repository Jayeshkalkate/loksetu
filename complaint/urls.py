from django.urls import path
from . import views

app_name = 'complaint'

urlpatterns = [
    path('', views.complaint_view, name='complaint'),
    path('track/', views.track_complaint, name='track_complaint'),
    path('result/<str:complaint_id>/', views.complaint_result, name='complaint_result'),
    path('map/', views.map_complaint, name='map_complaint'),

    # Authenticated/admin actions
    path('detail/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('mark-read/<str:complaint_id>/', views.mark_complaint_read, name='mark_complaint_read'),
    path('resolve/<str:complaint_id>/', views.resolve_complaint, name='resolve_complaint'),
    path('close/<str:complaint_id>/', views.close_complaint, name='close_complaint'),
    path('reject/<str:complaint_id>/', views.reject_complaint, name='reject_complaint'),
]