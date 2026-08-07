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


@app.get("/ranking")
def ranking_endpoint():
    prs_mergeados = merged_prs(OWNER, REPO, TOKEN)
    ranking = build_ranking(prs_mergeados)
    
    return {
        "repositorio": f"{OWNER}/{REPO}",
        "total_merges": len(prs_mergeados), # <-- Alteração semântica correta
        "quantidade_contribuidores": len(ranking),
        "ranking_top_contribuidores": ranking
    }