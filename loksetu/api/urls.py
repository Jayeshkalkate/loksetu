from django.urls import path
from .views import (
    CitizenAPIView,
    ComplaintAPIView,
    SchemeAPIView,
    ProjectAPIView,
    FundAPIView,
    ComplaintDetailAPIView,
    SchemeDetailAPIView,
    FundDetailAPIView,
    ProjectDetailAPIView,
)

app_name = "api"

urlpatterns = [
    # List/Create endpoints
    path("citizens/", CitizenAPIView.as_view(), name="citizen-list"),
    path("complaints/", ComplaintAPIView.as_view(), name="complaint-list"),
    path("schemes/", SchemeAPIView.as_view(), name="scheme-list"),
    path("projects/", ProjectAPIView.as_view(), name="project-list"),
    path("funds/", FundAPIView.as_view(), name="fund-list"),

    # Detail endpoints (optional)
    path("complaints/<int:pk>/", ComplaintDetailAPIView.as_view(), name="complaint-detail"),
    path("schemes/<int:pk>/", SchemeDetailAPIView.as_view(), name="scheme-detail"),
    path("funds/<int:pk>/", FundDetailAPIView.as_view(), name="fund-detail"),
    path("projects/<int:pk>/", ProjectDetailAPIView.as_view(), name="project-detail"),
]