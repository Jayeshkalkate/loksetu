from django.urls import path
from . import views

urlpatterns = [
    path('file/', views.file_complaint, name='file_complaint'),
    path('track/', views.track, name='track'),
    path('history/', views.history, name='history'),
    path('map/', views.complaint_map, name='complaint_map'),
    path('map/data/', views.map_data, name='map_data'),
    path('<str:cid>/', views.detail, name='complaint_detail'),
]
