from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests                                                    #requests serve para fazer requisições HTTP
import os                                                           
from collections import Counter                                     
from dotenv import load_dotenv


load_dotenv()

app = FastAPI ()

# --- CONFIGURAÇÃO DO CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Na fase de testes, permite conexões de qualquer front-end
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],
)
# ----------------------------

OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
TOKEN = os.getenv("TOKEN")

def merged_prs(owner, repo, token):
    dados = []
    page = 1
# Laço infinito controlado que varre as páginas
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {"Authorization": f"Bearer {token}"}
# Otimiza a busca pedindo 100 de vez e controlando a página atual
        params = {"state": "closed", "per_page": 100, "page": page}

        response = requests.get(url, headers=headers, params=params)    
        if response.status_code != 200:         # 200 = Sucesso
            break
            
        prs = response.json()

        if not prs:                             # Condição de parada (fim dos dados)
            break
        for pr in prs:
            if pr.get("merged_at") is not None: # Garante que o código foi integrado a partir da data e hora do merge
                dados.append(pr)
        
        page += 1                               # Avança para a próxima página

    return dados

# Extração de contribuidores e quantidade
def build_ranking(prs):
    # Extrai apenas os nomes e conta tudo automaticamente e de forma otimizada
    contributors = [pr["user"]["login"] for pr in prs]
    return Counter(contributors).most_common()


# ROTA DA API: Aqui é onde o usuário bate quando acessa a web
@app.get("/ranking")
def ranking_endpoint():
    # 1. Pega os PRs usando as variáveis globais
    prs_mergeados = merged_prs(OWNER, REPO, TOKEN)
    
    # 2. Gera o ranking
    ranking = build_ranking(prs_mergeados)
    
    # 3. Retorna um JSON formatado e bonito para o usuário
    return {
        "repositorio": f"{OWNER}/{REPO}",
        "total_prs_aprovados": len(prs_mergeados),
        "quantidade_contribuidores": len(ranking),
        "ranking_top_contribuidores": ranking
    }

"""
A função 'merged_prs' só pode ser inicializada com os parâmetros 'owner, repo, token';

Todas as informações que a api do github passar serão armazenadas na lista 'dados', os dados serão lidos de 100 em 100 como está dito na variável 'params', para acessar o github é necessário o 'TOKEN' que o próprio github fornece;

Criamos uma variável response para hospedar a requisição https (requests.get) que é composta pela url, os 'headers' e os 'params'. Se response diferente de Sucesso (200), quebra o código;

Criamos 'prs' para armazenar o json que a api do github nos entregar. Armazenando em uma variável do python, o prórpio python agora, consegue alterar tudo o que estiver dentro, livremente. Caso a varável 'prs' esteja vazia, quer dizer que acabaram as infos do site e o loop quebra.

Nova variável 'pr', portanto para toda 'pr' e 'prs', se a data do merge não estiver vazia (se houver data de merge) o merge é adicionado 'append' à variável 'pr'. O ciclo volta e somando 1 a página, por isso é necessário no início registrar 'page = 1'.

Contribuidores fica guardado na lista 'contributors'

'Counter' conta quantas vezes aparece o nome de cada contribuidor
"""
