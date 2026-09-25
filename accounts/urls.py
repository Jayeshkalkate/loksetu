from django.contrib.auth import views as auth
from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/done/', auth.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
