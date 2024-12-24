
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetView

urlpatterns = [
    path('login/', views.LoginView, name='login'),
    path('signup/', views.SignupView, name='signup'),
    path('user_dashboard/', views.UserDashboardView, name='user_dashboard'),
    
    path('logout/', views.LogoutView, name='logout'),

 
    path('password_reset/', views.password_reset, name='password_reset'),

    path('password_reset_confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),


]