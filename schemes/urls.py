from django.urls import path
from . import views

urlpatterns = [

    path('schemes/', views.schemes, name='schemes'),
    path("verify-scheme/<int:scheme_id>/", views.verify_scheme, name="verify_scheme"),
]