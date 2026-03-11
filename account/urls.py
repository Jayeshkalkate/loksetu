from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    path('password_reset_form/', views.password_reset_form, name='password_reset_form'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
    
    
    path('state_admin_dashboard/', views.state_admin_dashboard, name='state_admin_dashboard'),
    path('super_admin_dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    
    path('create-state-admin/', views.create_state_admin, name='create_state_admin'),
    
    path("verify-scheme/<int:scheme_id>/", views.verify_scheme, name="verify_scheme"),
    
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path("profile/", views.profile, name="profile"),
   
]
