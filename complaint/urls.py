from django.urls import path
from . import views

urlpatterns = [

    path('Complaint/', views.Complaint_view, name='Complaint'),

    path('track-Complaint/', views.track_Complaint, name='track_Complaint'),

    # path('Complaint-result/<int:Complaint_id>/', views.Complaint_result, name='Complaint_result'),
    path('Complaint-result/<str:Complaint_id>/', views.Complaint_result, name='Complaint_result'),

    path('map-Complaint/', views.map_Complaint, name='map_Complaint'),
    
    path('mark-read/<str:Complaint_id>/', views.mark_Complaint_read, name='mark_Complaint_read'),
    
    path("resolve/<str:Complaint_id>/", views.resolve_Complaint, name="resolve_Complaint"),
    path("close/<str:Complaint_id>/", views.close_Complaint, name="close_Complaint"),
    path("detail/<str:Complaint_id>/", views.Complaint_detail, name="Complaint_detail"),

]
