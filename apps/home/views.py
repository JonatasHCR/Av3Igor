from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# Create your views here.
@login_required
def home(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    if request.method == "POST":
        code_area = request.POST.get('botao')
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/{code_area}/List'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        
        banco = pd.DataFrame(dados)
        cont = 0
        for colunas in banco[['title',"description"]].values:
            banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
            cont += 1

        return render(request,'home.html',{"dados_area": banco.to_dict(orient='records')})
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    
    banco = pd.DataFrame(dados)
    
    return render(request,'home.html',{"dados": banco.to_dict(orient='records')})

#pesquisa pelo objetivo
@login_required
def home_objetivo(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    if request.method == "POST":
        code_goal = request.POST.get('botao')
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/{code_goal}/GeoAreas'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        
        banco = pd.DataFrame(dados)
        cont = 0

        return render(request,'home.html',{"dados": banco.to_dict(orient='records')})
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    
    banco = pd.DataFrame(dados)
    cont = 0
    for colunas in banco[['title',"description"]].values:
        banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
        cont += 1
    
    return render(request,'home.html',{"dados_area": banco.to_dict(orient='records'), 'obj': True})