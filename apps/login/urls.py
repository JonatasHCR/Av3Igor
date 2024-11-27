from django.urls import path
from .views import entrar

urlpatterns = [
    path('', entrar, name='login'),
]