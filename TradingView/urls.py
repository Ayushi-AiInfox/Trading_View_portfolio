from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

# View for the root path to redirect to the login page
def root_redirect(request):
    
    return HttpResponseRedirect('accounts/login')    
    

urlpatterns = [
    path('admin/', include('admin.urls')),
    path('', root_redirect, name='root'),  
    path('accounts/', include('accounts.urls')),  
]



# urlpatterns = [
#     path('admin/', include(('admin.urls', 'admin'), namespace='admin')),
#     path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
# ]