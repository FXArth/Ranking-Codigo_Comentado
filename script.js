            // Data
            const currentDate = new Date();
            const year = currentDate.getFullYear();
            const month = String(currentDate.getMonth() + 1).padStart(2, '0');
            const day = String(currentDate.getDate()).padStart(2, '0');
            const date = document.getElementById('current-date');
            date.innerHTML = `${day}/${month}/${year}`;

            const diasFaltantes = 90 - Number(day);
            document.getElementById('days-left').innerText = `Faltam ${diasFaltantes > 0 ? diasFaltantes : 0} dias para o fechamento`;

            // Função ÚNICA e definitiva
            async function carregarRanking() {
                try {
                    // TRUQUE SÊNIOR: Define a URL correta dependendo se está no PC ou na nuvem
                    const API_URL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
                        ? "http://127.0.0.1:8000/ranking"
                        : "https://ranking-codigo-comentado.onrender.com/ranking";

                    const response = await fetch(API_URL);
                    const data = await response.json();

                    // 1. Injetando os dados dos Cards
                    document.getElementById("star-count").innerText = data.estrelas_totais || 0;
                    document.getElementById("total-participantes").innerText = data.quantidade_contribuidores;
                    document.getElementById("total-merges").innerText = data.total_merges;

                    const ranking = data.ranking_top_contribuidores;

                    // 2. Injetando dados no Pódio (Agora lendo propriedades do Dicionário)
                    if (ranking.length > 0) {
                        const nome1 = ranking[0].nome;
                        document.getElementById("nome-primeiro").innerHTML = `<a href="https://github.com/${nome1}" target="_blank" class="github-link">${nome1}</a> <br> <strong> <span style="font-size: 0.8em; color: #D3AF37;">${ranking[0].xp} XP</span>`;
                    }
                    if (ranking.length > 1) {
                        const nome2 = ranking[1].nome;
                        document.getElementById("nome-segundo").innerHTML = ` <a href="https://github.com/${nome2}" target="_blank" class="github-link">${nome2}</a> <br> <strong> <span style="font-size: 0.8em; color: #CBC9C1;">${ranking[1].xp} XP</span>`;
                    }
                    if (ranking.length > 2) {
                        const nome3 = ranking[2].nome;
                        document.getElementById("nome-terceiro").innerHTML = `<a href="https://github.com/${nome3}" target="_blank" class="github-link">${nome3}</a> <br> <strong> <span style="font-size: 0.8em; color: #9E4C00;">${ranking[2].xp} XP</span>`;
                    }

                    // 3. Montando a Tabela Geral
                    const tabelaCorpo = document.getElementById("tabela-corpo");
                    tabelaCorpo.innerHTML = "";

                    const rankingGeral = ranking.slice(3);

                    rankingGeral.forEach((contribuinte, index) => {
                        const posicao = index + 4;
                        const linha = document.createElement("tr");

                        // Lógica nova: gerando 5 colunas para a tabela bater com o cabeçalho
                        linha.innerHTML = `
                            <td>${posicao}</td>
                            <td><a href="https://github.com/${contribuinte.nome}" target="_blank" class="github-link">${contribuinte.nome}</a></td>
                            <td>${contribuinte.merges}</td>
                            <td>${contribuinte.reviews}</td>
                            <td class="destaque-xp">${contribuinte.xp} XP</td>
                        `;
                        tabelaCorpo.appendChild(linha);
                    });

                } catch (erro) {
                    console.error("Erro ao conectar com a API:", erro);
                    document.getElementById("tabela-corpo").innerHTML = `
                        <tr>
                            <td colspan="5" style="text-align: center; color: red;">
                                Erro ao carregar os dados. Verifique se o servidor FastAPI está rodando.
                            </td>
                        </tr>   
                    `;
                }
            }

            carregarRanking();

            // Busca
            const inputBusca = document.getElementById('busca-ranking');
            inputBusca.addEventListener('input', function () {
                const termo = this.value.toLowerCase();
                const linhas = document.querySelectorAll('#tabela-corpo tr');

                linhas.forEach(linha => {
                    const nome = linha.children[1].textContent.toLowerCase();
                    if (nome.includes(termo)) {
                        linha.style.display = '';
                    } else {
                        linha.style.display = 'none';
                    }
                });
            });