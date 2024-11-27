from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests

# Create your views here.
@login_required
def home(request):
    url = ''
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    return render(request,'home.html',{"dados": dados})