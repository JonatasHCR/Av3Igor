from django.urls import path
from .views import home, home_objetivo, home_grafico

urlpatterns = [
    path('', home, name='home'),
    path('objetivo', home_objetivo, name='objetivo'),
    path('grafico', home_grafico, name='grafico'),
]