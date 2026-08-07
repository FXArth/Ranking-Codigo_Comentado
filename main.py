from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests                                                    
import os                                                           
from collections import Counter                                     
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- CONFIGURAÇÃO DO CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
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
        if response.status_code != 200:         
            print(f"🚨 ERRO DO GITHUB: Status {response.status_code} | Detalhe: {response.text}")
            break
            
        prs = response.json()

        if not prs:                             
            break
            
        for pr in prs:
            if pr.get("merged_at") is not None: 
                dados.append(pr)
        
        page += 1                               

    return dados


# --- REGRA DE NEGÓCIOS: Extração e Filtro de Contribuidores ---
def build_ranking(prs):
    # 1. Definimos quem são os mantenedores que não devem competir
    mantenedores = ["FXArth", "Morcineck", "ohlm1"]

    # 2. Extrai os nomes, mas IGNORA quem estiver na lista acima
    contributors = [
        pr["user"]["login"] 
        for pr in prs 
        if pr["user"]["login"] not in mantenedores
    ]
    
    # 3. Conta e monta o ranking apenas com a comunidade
    return Counter(contributors).most_common()


# ROTA DA API: Aqui é onde o usuário bate quando acessa a web
@app.get("/ranking")
def ranking_endpoint():
    # 1. Pega os PRs usando as variáveis globais
    prs_mergeados = merged_prs(OWNER, REPO, TOKEN)
    
    # 2. Gera o ranking (agora sem os mantenedores)
    ranking = build_ranking(prs_mergeados)
    
    # 3. Retorna um JSON formatado e bonito para o usuário
    return {
        "repositorio": f"{OWNER}/{REPO}",
        "total_prs_aprovados": len(prs_mergeados),
        "quantidade_contribuidores": len(ranking),
        "ranking_top_contribuidores": ranking
    }