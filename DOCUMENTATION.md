**Visão Geral (focada na versão Python)**

Este documento descreve somente a versão Python do NavGrafo UFG (pasta `versao Python`). Contém explicações detalhadas sobre as estruturas de dados, os carregadores de mapas, o algoritmo de menor caminho implementado e a integração com a interface Pygame — material pronto para apresentação.

**Arquivos relevantes (versão Python)**
- [versao Python/main.py](versao%20Python/main.py) — aplicação principal e orquestrador da GUI.
- [versao Python/core.py](versao%20Python/core.py#L1-L200) — estruturas de dados (`Vertice`, `Grafo`) e carregadores (`carregar_poly`, `carregar_txt`, `carregar_osm_xml`).
- [versao Python/algorithms.py](versao%20Python/algorithms.py#L1-L200) — algoritmo de Dijkstra e utilitários de medição.
- [versao Python/gui.py](versao%20Python/gui.py) — componentes visuais (botões, câmera, cores, constantes).

**Resumo do Fluxo de Dados (Python)**
- Entrada: `.poly`, `.txt` (estruturado) e `.osm/.xml` (OSM). O módulo `core.py` detecta o formato e chama o carregador adequado via `carregar_grafo`.
- Parsing: os carregadores populam uma instância de `Grafo` com vértices projetados em coordenadas planas e arestas com peso igual à distância euclidiana entre vértices.
- Cálculo: `algorithms.dijkstra` recebe a instância de `Grafo`, `inicio` e `fim`, e retorna `(caminho, distancia_total, nos_explorados, tempo_ms)`.
- Visualização: `main.py` usa `gui.py` para desenhar o grafo e exibir estatísticas; seleção de origem/destino, edição do grafo e disparo do cálculo são feitos na GUI.

**Estruturas de Dados — Detalhamento (em `core.py`)**

1) `Vertice`
- Implementado como classe com `__slots__ = ('id','x','y','label')` para reduzir overhead de memória.
- `id`: índice sequencial interno.
- `x,y`: coordenadas projetadas (metros).
- `label`: rótulo legível (opcional).

2) `Grafo`
- `vertices`: lista de `Vertice` ou `None` (quando removido).
- `adj`: lista de listas; `adj[u]` contém tuplas `(v, d, directed)` onde `d` é a distância euclidiana entre `u` e `v`, `directed` é booleano.
- `arestas_raw`: lista de tuplas `(u, v, directed)` usada pela GUI para iteração e edição.

Operações críticas (implementadas em `core.py`):
- `adicionar_vertice(x,y,label)` — retorna `vid`.
- `adicionar_aresta(u,v,directed=False)` — calcula a distância via `_dist` e adiciona entradas em `adj` e `arestas_raw`.
- `remover_aresta(u,v,directed=None)` — remove a primeira aresta compatível de `arestas_raw` e filtra as listas de adjacência.
- `remover_vertice(vid)` — marca `vertices[vid] = None` e limpa referências.

Observações de design:
- Lista de adjacência é eficiente para grafos esparsos; `arestas_raw` facilita desenho e manipulação pela interface.
- Limitações: remoção cria lacunas (requere checagem de `None` em loops); operações espaciais (busca de vértice/aresta mais próxima) fazem varredura completa — recomenda-se adicionar estrutura espacial (R-tree/Quadtree) se precisar escalar.

**Carregadores de mapas (detalhes implementacionais)**

- `carregar_poly(caminho_arq)`:
  - Formato: número de vértices, lista de vértices (id x y), número de arestas, lista de arestas (u v directed).
  - Constrói `vertices` e `adj` diretamente usando valores fornecidos.

- `carregar_txt(caminho_arq)`:
  - Formato com seções `VERTICES` e `ARESTAS`; aceita comentários com `#`, `//` ou `;`.
  - Mapeia IDs externos para índices internos com `mapa_ids` antes de adicionar arestas.

- `carregar_osm_xml(caminho_arq)`:
  - Streaming com `xml.etree.ElementTree.iterparse` para memória controlada.
  - Extrai nós (`node`) com `id, lat, lon` e ways (`nd` refs + `tag` map).
  - Filtra `ways` por `highway` (se presente); calcula `lat0, lon0` como média para projeção.
  - Projeta lat/lon para (x,y) via `_projetar_latlon` (aproximação esférica: raio da terra e cos(lat0)).
  - Cria sequência de vértices e arestas, tratando `oneway` e direções invertidas (`oneway='-1'`).

Observações de robustez: uso de `elem.clear()` durante `iterparse` evita consumo excessivo de memória em arquivos OSM grandes.

**Algoritmo de Menor Caminho (Dijkstra) — implementação em `algorithms.py`**

Pontos essenciais da implementação:
- Usa `heapq` como fila de prioridade (min-heap) de tuplas `(dist, vertice)`.
- Vetores auxiliares: `dist` (inicial INF), `prev` (reconstrução de caminho), `visited` (fixação) e contador `explorados`.
- Early exit: interrupção quando o vértice destino é extraído do heap (otimização significativa em muitos casos reais).
- Ignora vértices removidos (`grafo.vertices[v] is None`) durante relaxação.

Assinatura e retorno:
- `dijkstra(grafo, inicio, fim) -> (caminho, distancia_total, nos_explorados, tempo_ms)`.

Complexidade:
- Tempo: O((V + E) log V) com heap binário (implementação prática com `heapq`).
- Espaço: O(V + E) para grafo + O(V) para vetores auxiliares.

Sugestões de melhoria (para apresentação / trabalho futuro):
- Implementar A* usando heurística euclidiana: fácil adaptação sobre a estrutura atual e reduz nósexplorados em mapas geográficos.
- Busca bidirecional (dois Dijkstras simultâneos) para grafos grandes.
- Adição de índice espacial (R-tree / k-d tree) para acelerar seleções interativas (vertice/aresta mais próxima).

**Integração com a GUI (`main.py` / `gui.py`)**

- `main.py` mantém estado da aplicação: `grafo`, `cam` (Camera), `origem`, `destino`, `caminho`, métricas, e modos de interação (adicionar/remover vértices/arestas, pan, seleção).
- Seleção espacial: `vertice_mais_proximo` e `aresta_mais_proxima` percorrem listas (`vertices` / `arestas_raw`) e usam projeções tela↔mundo para comparar distâncias; custo O(V) ou O(E) por consulta.
- Desenho: `desenhar_grafo` usa `arestas_raw` para traçar arestas e `adj` para pesos; estilo (cores, espessura) muda se o elemento pertence ao caminho calculado.

Comandos para executar (Windows / PowerShell):

```powershell
python -m pip install pygame
cd "versao Python"
python main.py
```

**Exemplos de medidas e testes para apresentação**
- Execute rotas entre pontos conhecidos no arquivo `Campus2UFG&Regiao.osm` (presente na pasta `versao Python`) e apresente:
  - `distancia_total`, `nos_explorados`, e `tempo_ms` retornados por `dijkstra`.
  - Compare execução Dijkstra vs A* (implementar A* para comparação) em pelo menos 2 mapas com ~100 e ~1000 vértices.

**Roteiro de slides (focado em Python)**
- Slide 1 — Título: "NavGrafo UFG — Versão Python" (objetivo da versão Python)
- Slide 2 — Arquitetura: `core.py` → `algorithms.py` → `main.py`/`gui.py` (diagrama)
- Slide 3 — Estruturas: `Vertice` e `Grafo` (mostrar exemplo de `adj` e `arestas_raw`)
- Slide 4 — Carregamento OSM: `carregar_osm_xml` e projeção (`_projetar_latlon`)
- Slide 5 — Dijkstra: pseudocódigo e pontos de implementação (heapq, early exit, vértices removidos)
- Slide 6 — Métricas experimentais: `nos_explorados` e `tempo_ms` (tabelas/gráficos sugeridos)
- Slide 7 — Limitações e melhorias propostas (A*, R-tree, bidirecional)
- Slide 8 — Demonstração: executar `main.py` e carregar `Campus2UFG&Regiao.osm`
- Slide 9 — Conclusão e próximos passos

---

Se quiser, eu posso agora:
- Gerar slides em Markdown prontos para converter para PPTX.
- Implementar e adicionar uma versão A* em `versao Python/algorithms.py` com comparação automática.
- Implementar uma R-tree simples (via `rtree` ou `pygeos`) para acelerar buscas interativas.

Diga qual opção prefere e eu executo o próximo passo.
