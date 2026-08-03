"""
TEMA: Consumo de API e Manipulação de Dados (Ranking de PRs)

Nível:
🟡 Intermediário

Autor: Arthur Brito
Última atualização: 24/07/2026
Pré-requisitos: Lógica de programação básica, noções de HTTP e Listas/Dicionários
Tempo estimado de leitura: 12 min

O QUE É?
O ranking é uma automação em Python que se conecta
à API REST oficial do GitHub. A automação puxa o histórico de
Pull Requests (PRs) de um repositório, identifica as PRs que foram realmente integrados ao projeto (merged) e gera um placar, contabilizando os maiores contribuidores.

COMO FUNCIONA?
O código utiliza a biblioteca requests para enviar requisições
HTTP (GET) aos servidores do GitHub. O Github por sua vez, não devolve
todo o histórico de uma vez, o script usa um laço de repetição (while)
para buscar o histórico do projeto página por página. Por fim, ele utiliza
a ferramenta nativa Counter (ferramenta que já vem junto da linguagem python) para contabilizar e ordenar a quantidade de vezes que cada desenvolvedor aparece na lista.

POR QUE EXISTE?
Controlar as contribuições de cada participante via web é inviável dependendo do tamanho do projeto. Scripts como este existem para automatizar a extração de dados, permitindo que a equipe que gerencia o projeto ganhe tempo e tenha métricas já prontas para relatórios, sabendo assim quem pode recompensar e/ou prestar suporte.

QUANDO USAR?
Sempre que precisar fazer uma vistoria rápida sobre o engajamento
da comunidade ou de uma equipe técnica em um repositório,
ou quando quiser integrar esses dados de contribuição em como planilhas ou dashboards.

QUANDO NÃO USAR?
Caso o objetivo seja analisar o conteúdo do código (linhas alteradas, impacto na arquitetura), pois o ranking tras apenas uma "lista" de PRs. Para isso seriam mais adequadas ferramentas de análise estática.

VANTAGENS
Automação rápida e escalável.
Pode ser facilmente adaptado para filtrar por datas, labels ou equipes.
Código leve, dependendo de poucas bibliotecas externas.

DESVANTAGENS
Limitado pelas regras de Rate Limit (limite de requisições) da API do GitHub.
Repositórios gigantescos podem levar muito tempo para serem processados devido à necessidade de requisições sequenciais.

ERROS MAIS COMUNS
Esquecer de enviar o Token de Autenticação nos "Headers",
que é limitado para usuários anônimos (Erro 403).
Não tratar a paginação, o que resulta na leitura de apenas uma pequena fração do histórico real (geralmente os últimos 30 PRs).
Não verificar se a resposta HTTP teve sucesso (código 200) antes de tentar extrair o JSON.
Não fazer a filtragem de PRs "Merged" e de PRs apenas "Fechados/Rejeitados"

BOAS PRÁTICAS
Use variáveis de ambiente (como arquivos .env) para guardar seu Token, nunca o deixando exposto no código fonte.
Utilize parâmetros como per_page=100 para otimizar as chamadas de rede (trazendo mais itens de uma só vez).

ANALOGIA
Imagine que o repositório é uma biblioteca pública e os PRs
são registros de livros doados. A API do GitHub é a bibliotecária.
Em vez de contar os livros na estante, você entrega sua
carteirinha (Token) à bibliotecária e pede os registros. Como os
registros são muitos, ela te entrega um caderno de cada vez (Paginação).
Você anota tudo e entrega para um contador ágil (o Counter),
que te devolve o ranking pronto de quem doou mais.

RESUMO
O script combina requisições HTTP seguras, lógica de paginação
e estruturas de dados otimizadas do Python para extrair,
filtrar e ranquear automaticamente os dados de colaboração
de um repositório hospedado no GitHub.
"""
#EXEMPLO PRÁTICO

#CÓDIGO CORRETO

import requests
from collections import Counter

# Suas configurações (mantenha as mesmas)
OWNER = "[DONO DO REPOSITÓRIO]"
REPO = "[REPOSITÓRIO]"
TOKEN = "[TOKEN]"

def get_merged_prs(owner, repo, token):
    merged_prs = []
    page = 1
    
    # Loop infinito controlado que varre as páginas
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls" # URL 
        headers = {"Authorization": f"Bearer {token}"}
        
        # Otimiza a busca pedindo 100 por página e controlando a página atual
        params = {"state": "closed", "per_page": 100, "page": page}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:         # 200 = Sucesso // 404 = Not Found...
            break
            
        prs = response.json()
        
        if not prs:                             # Caso não haja mais resposta do site (fim dos dados)
            break                               # Quebra
            
        for pr in prs:
            if pr.get("merged_at") is not None: # Garante que o código foi integrado a partir da data e hora do merge
                merged_prs.append(pr)
        
        page += 1                               # Avança para a próxima página
        
    return merged_prs

def build_ranking(prs):
    # Extrai apenas os nomes e conta tudo automaticamente e de forma otimizada
    contributors = [pr["user"]["login"] for pr in prs]
    return Counter(contributors).most_common()

"""
Explicação escrita:
O código correto lida perfeitamente com a infraestrutura do GitHub. Ele usa
um laço while combinado com o parâmetro page para não deixar nenhum
dado para trás. A validação pr.get("merged_at") is not None é crucial,
pois a API agrupa PRs rejeitados e aceitos sob o mesmo status "closed".
Por fim, o uso do Counter substitui dezenas de linhas de código manual,
transformando a lista de nomes em um ranking ordenado instantaneamente.
"""
#CÓDIGO INCORRETO

import requests

def get_prs_errado(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed"
    
    # ERRO 1: Nenhuma autenticação enviada. O limite será de 60 requisições/hora.
    # ERRO 2: Nenhuma paginação. Vai pegar apenas os 30 últimos PRs (padrão da API).
    resposta = requests.get(url)
    prs = resposta.json() 
    
    ranking = {}
    for pr in prs:
        # ERRO 3: Pega todos os PRs fechados, incluindo os rejeitados/lixo.
        autor = pr["user"]["login"]
        
        # ERRO 4: Lógica manual e verbosa para contar ocorrências.
        if autor in ranking:
            ranking[autor] += 1
        else:
            ranking[autor] = 1
            
    return ranking

"""
Explicação escrita:
Este código possui falhas críticas para um ambiente de produção. A falta de
um "Header" com o Token reduzirá drasticamente o uso da API. A ausência de
parâmetros de paginação e o limite de itens (per_page) fará com que o
script conte apenas uma pequena fração recente do histórico, gerando um ranking
falso. Além disso, o laço de repetição conta PRs que foram cancelados pelos
administradores (sem merge), premiando contribuições que nunca entraram no
projeto de fato.

=============================================================
DESAFIO
Altere a função get_merged_prs do "Código Correto" para
receber um novo parâmetro chamado ano_alvo. O script deve
agora filtrar e ranquear apenas os Pull Requests que foram
"mergeados" no ano passado (ex: 2025).
Dica: O campo merged_at retorna uma string ISO 8601
(ex: "2025-11-20T15:00:00Z").

=============================================================
VOCÊ SABIA? (opcional)
A classe Counter que usamos no script correto não é apenas
"código mais limpo". Por trás dos panos, ela é implementada em
C (a linguagem base do Python), o que a torna ordens de grandeza
mais rápida para processar milhares de itens do que montar a
contagem manualmente com ifs e dicionários tradicionais!

=============================================================
REFERÊNCIAS
Documentação da API do GitHub (Pulls): https://docs.github.com/en/rest/pulls/pulls

Biblioteca Requests: https://requests.readthedocs.io/

Collections / Counter: https://docs.python.org/3/library/collections.html#collections.Counter
=============================================================
"""