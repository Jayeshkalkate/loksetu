from django.urls import path

from .views import (
    CitizenAPIView,
    ComplaintAPIView,
    SchemeAPIView,
    ProjectAPIView,
    FundAPIView,
)

urlpatterns = [
    path('citizens/', CitizenAPIView.as_view()),
    path('complaints/', ComplaintAPIView.as_view()),
    path('schemes/', SchemeAPIView.as_view()),
    path('projects/', ProjectAPIView.as_view()),
    path('funds/', FundAPIView.as_view()),
]