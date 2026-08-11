from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests                                             
import os                                                   
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
TOKEN = os.getenv("TOKEN")
# Transformamos o repositório único em uma lista para o sistema Multi-repo
REPOS = ["Codigo_comentado"] 

def merged_prs_multi_repo(owner, repos, token):
    dados = []
    headers = {"Authorization": f"Bearer {token}"}
        
    # Laço de repetição para varrer todos os repositórios da lista
    for repo in repos:
        page = 1
        while True:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            params = {"state": "closed", "per_page": 100, "page": page}

            response = requests.get(url, headers=headers, params=params)    
            if response.status_code != 200:         
                print(f"🚨 ERRO DO GITHUB no repo {repo}: Status {response.status_code} | Detalhe: {response.text}")
                break
                
            prs = response.json()

            if not prs:                             
                break
                
            for pr in prs:
                if pr.get("merged_at") is not None: 
                    # Injetamos a origem do PR para calcular o XP corretamente depois
                    pr["origem_repo"] = repo.lower()
                    dados.append(pr)
            
            page += 1                               

    return dados


def build_ranking(prs):
    mantenedores = ["fxarth", "morcineck", "ohlm1"]
    xp_bank = {} # O nosso novo Dicionário de XP

    for pr in prs:
        author = pr["user"]["login"].lower()
        repo_source = pr.get("origem_repo", "")

        # 1. Gamificação para os Autores (Merges)
        if author not in mantenedores:
            if author not in xp_bank:
                xp_bank[author] = {"xp": 0, "merges": 0, "reviews": 0}
            
            xp_bank[author]["merges"] += 1
            
            # Regras de negócio de base 100
            if repo_source == "projetos":
                xp_bank[author]["xp"] += 100
            elif repo_source == "aulas":
                xp_bank[author]["xp"] += 200
            else:
                xp_bank[author]["xp"] += 100

        # 2. Gamificação para os Avaliadores (Reviews)
        for label in pr.get("labels", []):
            label_name = label["name"].lower()
            
            # O código procura pela label mágica "review-"
            if label_name.startswith("review-"):
                reviewer = label_name.replace("review-", "").strip()
                
                if reviewer not in mantenedores:
                    if reviewer not in xp_bank:
                        xp_bank[reviewer] = {"xp": 0, "merges": 0, "reviews": 0}
                    
                    xp_bank[reviewer]["reviews"] += 1
                    xp_bank[reviewer]["xp"] += 100 # Bonificação do review

    # Converte o dicionário em uma lista ordenada com quem tem mais XP no topo
    ranking_ordenado = sorted(
        [{"nome": k, **v} for k, v in xp_bank.items()],
        key=lambda x: x["xp"],
        reverse=True
    )
    
    return ranking_ordenado


def obter_estrelas_multi_repo(owner, repos, token):
    """Busca a quantidade de estrelas somada de todos os repositórios."""
    total_estrelas = 0
    headers = {"Authorization": f"Bearer {token}"}
    
    for repo in repos:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        resposta = requests.get(url, headers=headers)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            total_estrelas += dados.get("stargazers_count", 0)
        else:
            print(f"Erro ao buscar estrelas do repo {repo}: {resposta.status_code}")
            
    return total_estrelas


@app.get("/ranking")
def ranking_endpoint():
    prs_mergeados = merged_prs_multi_repo(OWNER, REPOS, TOKEN)
    ranking = build_ranking(prs_mergeados)
    total_estrelas = obter_estrelas_multi_repo(OWNER, REPOS, TOKEN)
    
    return {
        "organizacao": OWNER,
        "repositorios_rastreados": REPOS,
        "total_merges": len(prs_mergeados), 
        "quantidade_contribuidores": len(ranking),
        "estrelas_totais": total_estrelas,
        "ranking_top_contribuidores": ranking 
    }