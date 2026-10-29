from django.urls import path
from .views import register_participant, contact_view

urlpatterns = [
    path('api/register/', register_participant, name='register_participant'),
    path('api/register-boys/', register_participant, name='register_boys'),
    path('api/contact/', contact_view, name='contact_view'),
]