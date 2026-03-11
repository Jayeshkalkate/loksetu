from django.urls import path
from . import views

urlpatterns = [

    path('complaint/', views.complaint_view, name='complaint'),

    path('track-complaint/', views.track_complaint, name='track_complaint'),

    # path('complaint-result/<int:complaint_id>/', views.complaint_result, name='complaint_result'),
    path('complaint-result/<str:complaint_id>/', views.complaint_result, name='complaint_result'),

    path('map-complaint/', views.map_complaint, name='map_complaint'),
    
    path('mark-read/<str:complaint_id>/', views.mark_complaint_read, name='mark_complaint_read'),
    
    path("resolve/<str:complaint_id>/", views.resolve_complaint, name="resolve_complaint"),

]