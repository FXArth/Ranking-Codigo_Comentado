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
    
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {"Authorization": f"Bearer {token}"}
        
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


def build_ranking(prs):
    mantenedores = ["fxarth", "morcineck", "ohlm1"]

    contributors = [
        pr["user"]["login"] 
        for pr in prs 
        if pr["user"]["login"].lower() not in mantenedores
    ]
    
    return Counter(contributors).most_common()

def obter_estrelas_repositorio(owner, repo, token):
    """Busca a quantidade de estrelas de um repositório específico."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    
    # Criamos o cabeçalho aqui dentro usando o seu token!
    headers = {"Authorization": f"Bearer {token}"}
    
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        return dados.get("stargazers_count", 0)
    else:
        print(f"Erro ao buscar estrelas: {resposta.status_code}")
        return 0

@app.get("/ranking")
def ranking_endpoint():
    prs_mergeados = merged_prs(OWNER, REPO, TOKEN)
    ranking = build_ranking(prs_mergeados)
    
    # 1. Executamos a função passando OWNER, REPO e também o TOKEN
    total_estrelas = obter_estrelas_repositorio(OWNER, REPO, TOKEN)
    
    return {
        "repositorio": f"{OWNER}/{REPO}",
        "total_merges": len(prs_mergeados), 
        "quantidade_contribuidores": len(ranking),
        "ranking_top_contribuidores": ranking,
        "estrelas": total_estrelas 
    }