from django.urls import path
from . import views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views

urlpatterns = [
  
    path('dashboard/', views.AdminDashboardView, name='admin_dashboard'),
    path('save-symbol/', views.SaveSymbol,name= 'saving_symbol'),
    path('save-interval/',views.saveInterval,name='save interval'),
    path('profile/',views.profile,name='profile'),
    path("screen-2/",views.screen2,name='screen2'),
    path("screen-3/",views.screen3,name="screen3"),
    path("save-multi-symbol/",views.save_multi_screen,name="save_multi_symbols"),
    path('portfolio/',views.portfolio_performance_view,name='portfolio screen')

]

