from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import pandas as pd
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend não interativo
import os
from pathlib import Path

CAMINHO = Path(__file__).parent.parent.parent


# Create your views here.
@login_required
def home(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    
    banco = pd.DataFrame(dados)
    if request.method == "POST":
        name_area = request.POST.get('nome')
        colunas = banco.loc[banco['geoAreaName'] == name_area]
        code_area = colunas['geoAreaCode'].values
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/{code_area}/List'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        obj_quant = len(dados)
        banco = pd.DataFrame(dados)
        
        url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/List'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        
        total_obj = len(dados)
        
        cont = 0
        for colunas in banco[['title',"description"]].values:
            banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
            cont += 1
        # Dados
        labels = ["Objetivo Adotados", "Objetivos Não Adotados"]
        cores = ['green', 'red']
        # Criando o gráfico de pizza
        plt.pie([obj_quant,total_obj-obj_quant], labels=labels, autopct='%1.1f%%', startangle=90, colors=cores)
        name_area = tradutor.translate(name_area)
        # Adicionando título
        plt.title(f'Gráfico dos Objetivos Adotados por {name_area}')
         # Adicionando legenda
        plt.legend(labels, title="Categorias", loc="best")
        # Exibindo o gráfico
        plt.savefig(os.path.join(CAMINHO,'static','graficos','grafico.png'), dpi=100, bbox_inches='tight')
        plt.clf()
    
        return render(request,'home.html',{"dados_area": banco.to_dict(orient='records'), "nome": name_area, "img": os.path.join('graficos','grafico.png')})
    
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


#Gráficos
@login_required
def home_grafico(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    total_paises = len(dados)

    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    
    banco = pd.DataFrame(dados)
    banco_quant = pd.DataFrame(columns=['paises_tem', 'paises_nao'])
    cont = 0
    for codes in banco['code'].values:
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/{codes}/GeoAreas'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        
        paises_tem = len(dados)
        paises_nao = total_paises - paises_tem
        banco_quant.loc[cont] = [paises_tem, paises_nao]
        cont+=1
    
    cont = 0
    for colunas in banco[['title',"description"]].values:
        banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
        cont += 1
    
    banco = banco.join(banco_quant)
    # Dados
    labels = ["Tem o Objetivo", "Não Tem"]
    cores = ['green', 'red']
    cont = 1
    img = []
    for valores in banco[['paises_tem','paises_nao']].values:
        # Criando o gráfico de pizza
        plt.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90, colors=cores)

        # Adicionando título
        plt.title(f'Gráfico do objetivo {cont}')
         # Adicionando legenda
        plt.legend(labels, title="Categorias", loc="best")
        # Exibindo o gráfico
        plt.savefig(os.path.join(CAMINHO,'static','graficos',f'grafico{cont}.png'), dpi=100, bbox_inches='tight')
        plt.clf()
        img.append(os.path.join('graficos',f'grafico{cont}.png'))
        cont += 1 
    return render(request,'home_grafico.html',{"dados_area": zip(banco.to_dict(orient='records'), img), 'img': True})