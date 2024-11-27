from django.urls import path
from .views import cadastro

urlpatterns = [
    path('', cadastro, name='cadastro'),
]