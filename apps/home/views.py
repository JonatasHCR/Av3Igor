from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
import pandas as pd
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import matplotlib
import os
from pathlib import Path
#arquivo criado para enviar o email
from home.funcutil import enviar_email
#caminho para salvar na pasta static
CAMINHO = Path(__file__).parent.parent.parent
#caminho dos arquivos para ser enviado por email
CAMINHO_EMAIL = CAMINHO.parent.parent

matplotlib.use('Agg')  # Backend não interativo
# Create your views here.
#Pesquisa pelo país
@login_required#obrigando a ter usuário logado
def home(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    #pesquisando os países totais
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:

        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    #colocando os países num dataframe
    banco = pd.DataFrame(dados)
    
    if request.method == "POST":
        #verificando se foi apertado o botão de enviar email
        if request.POST.get('botao_enviar_email'):
            name_area = request.POST.get('botao_enviar_email')
        else:
            name_area =  request.POST.get('nome')
        #pesquisando o dataframe, o código do pais selecionado
        colunas = banco.loc[banco['geoAreaName'] == name_area]
        code_area = colunas['geoAreaCode'].values
        #pesquisando os objetivos do país
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/{code_area}/List'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        #salvando a quantidade de objetivos que o país tem
        obj_quant = len(dados)
        #salvando os dados do país em um dataframe
        banco = pd.DataFrame(dados)
        #pesquisando os objetivos totais
        url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/List'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        #salvando a quantidade de objetivos que tem disponível
        total_obj = len(dados)
        
        cont = 0
        #traduzindo o objetivo e sua descrição
        for colunas in banco[['title',"description"]].values:
            banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
            cont += 1
        # Dados
        labels = ["Objetivo Adotados", "Objetivos Não Adotados"]
        #cores
        cores = ['green', 'red']
        # Criando o gráfico de pizza
        plt.pie([obj_quant,total_obj-obj_quant], labels=labels, autopct='%1.1f%%', startangle=90, colors=cores)
        name_area = tradutor.translate(name_area)
        # Adicionando título
        plt.title(f'Gráfico dos Objetivos Adotados por {name_area}')
        # Adicionando legenda
        plt.legend(labels, title="Categorias", loc="best")
        # Salvando o gráfico em imagem
        plt.savefig(os.path.join(CAMINHO,'static','grafico','grafico.png'), dpi=100, bbox_inches='tight')
        #limpando para nao ocorrer sobreposição
        plt.clf()
        if request.POST.get('botao_enviar_email'):
            #pegando o email do usuário logado
            email_do_usuario = request.user.email
            #gerando tabela do dataframe
            banco[['title',"description"]].to_excel(os.path.join(CAMINHO,'static','grafico',"tabela.xlsx"), index=False)
            #ele tenta enviar o email caso consiga ou não ele exibe a mensagem de sucesso ou falha
            if not enviar_email(email_do_usuario,f'Gráfico referente ao país {name_area}',os.path.join(CAMINHO_EMAIL,'static','grafico')):
                #return com a mensagem do email de falha
                return render(request,'home.html',{"dados_area": banco.to_dict(orient='records'), "nome": name_area, "img": os.path.join('grafico','grafico.png'), "msg": "Não foi possível enviar o email"})
            #return com a mensagem do email de sucesso
            return render(request,'home.html',{"dados_area": banco.to_dict(orient='records'), "nome": name_area, "img": os.path.join('grafico','grafico.png'),"msg": "Email enviado com sucesso"})
        #return da seleção do país(POST)
        return render(request,'home.html',{"dados_area": banco.to_dict(orient='records'), "nome": name_area, "img": os.path.join('grafico','grafico.png')})
    #return para exibir os países(GET)
    return render(request,'home.html',{"dados": banco.to_dict(orient='records')})

#pesquisa pelo objetivo
@login_required#obrigando a ter usuário logado
def home_objetivo(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    
    if request.method == "POST":
        #pegando o código do objetivo
        code_goal = request.POST.get('botao')
        #pesquisando usando o código do objetivo
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/{code_goal}/GeoAreas'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        #salvando os países que tem aquele objetivo num dataframe
        banco = pd.DataFrame(dados)
        cont = 0
        #return dos dados referente ao objetivo escolhido(POST)
        return render(request,'home.html',{"dados": banco.to_dict(orient='records')})
    
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    #salvando os objetivos num dataframe
    banco = pd.DataFrame(dados)
    cont = 0
    #traduzindo os objetivos e sua descrição
    for colunas in banco[['title',"description"]].values:
        banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
        cont += 1
    #return dos dados traduzidos(GET)
    return render(request,'home.html',{"dados_area": banco.to_dict(orient='records'), 'obj': True})


#Gráficos dos objetivos
@login_required#obrigando a ter usuário logado
def home_grafico(request):
    tradutor = GoogleTranslator(source='en', target='pt')
    #pegando os países totais
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    #salvando a quantidade total
    total_paises = len(dados)
    #pegando o total de objetivos
    url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/List'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
        dados = response.json()  # Converte a resposta para JSON
    except requests.exceptions.RequestException as e:
        return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
    #salvando os objetivos num dataframe
    banco = pd.DataFrame(dados)
    #criando um dataframe vazio
    banco_quant = pd.DataFrame(columns=['paises_tem', 'paises_nao'])
    cont = 0
    #pesquisando cada objetivo
    for codes in banco['code'].values:
        url = f'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Goal/{codes}/GeoAreas'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levanta uma exceção se houver erro na requisição
            dados = response.json()  # Converte a resposta para JSON
        except requests.exceptions.RequestException as e:
            return render(request,'home.html',{"msg": f"Erro ao acessar a API: {e}"})
        #salvando a quantidade dos países que tem
        paises_tem = len(dados)
        #vendo quantos países não tem
        paises_nao = total_paises - paises_tem
        #adicionando no dataframe vazio criado anteriormente
        banco_quant.loc[cont] = [paises_tem, paises_nao]
        cont+=1
    
    cont = 0
    #traduzindo
    for colunas in banco[['title',"description"]].values:
        banco.loc[cont,['title',"description"]] = tradutor.translate(colunas[0]), tradutor.translate(colunas[1])
        cont += 1
    #juntando os dois dataframes
    banco = banco.join(banco_quant)
    # Dados
    labels = ["Tem o Objetivo", "Não Tem"]
    #cores
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
        # Criando imagem do gráfico de cada objetivo
        plt.savefig(os.path.join(CAMINHO,'static','graficos',f'grafico{cont}.png'), dpi=100, bbox_inches='tight')
        # Limpando
        plt.clf()
        #salvando o caminho para exibir no template
        img.append(os.path.join('graficos',f'grafico{cont}.png'))
        cont += 1
    #verificando se apertou o botão
    if request.POST.get('botao_enviar_email'):
            #pega o email do usuário logado
            email_do_usuario = request.user.email
            #transformando o dataframe numa tabela
            banco[['title',"description",'paises_tem',"paises_nao"]].to_excel(os.path.join(CAMINHO,'static','graficos',"tabela.xlsx"), index=False)
            #verificando se enviou ou nao o email
            if not enviar_email(email_do_usuario,f'Gráficos de cada objetivo\nMostrando o percentual de quantos países adotam aquele objetivo',os.path.join(CAMINHO_EMAIL,'static','graficos')):
                #return do email com falha
                return render(request,'home.html',{"dados_area": zip(banco.to_dict(orient='records'), img), 'img': True, "msg": "Não foi possível enviar o email"})
            #return do email com sucesso
            return render(request,'home_grafico.html',{"dados_area": zip(banco.to_dict(orient='records'), img), 'img': True, "msg": 'Email enviado com sucesso'})
    #return dos dados de cada objetivo(GET)
    return render(request,'home_grafico.html',{"dados_area": zip(banco.to_dict(orient='records'), img), 'img': True})