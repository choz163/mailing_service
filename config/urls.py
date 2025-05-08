from django.contrib import admin
from django.urls import path, include

urlpatterns = [

path('admin/', admin.site.urls),

path('accounts/', include('django.contrib.auth.urls')),

path('', include('mailings.urls', namespace='mailings')),

path('users/', include('users.urls')),

]