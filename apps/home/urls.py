from django.urls import path
from .views import home, home_objetivo

urlpatterns = [
    path('', home, name='home'),
    path('objetivo', home_objetivo, name='objetivo'),
]