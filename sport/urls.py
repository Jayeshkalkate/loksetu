from django.urls import path
from . import views

urlpatterns = [
    path('sport/', views.sport_events, name="sport_events"),
    path('verify-tournament/<int:id>/', views.verify_tournament, name="verify_tournament"),
]