from django.urls import path
from .views import entrar,sair

urlpatterns = [
    path('', entrar, name='login'),
    path('logout/', sair, name='logout'),
]