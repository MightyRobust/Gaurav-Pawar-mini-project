# C:\Users\acer\bkend\myproject\urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registrations.urls')),  # Forwards API calls to registrations/urls.py
]