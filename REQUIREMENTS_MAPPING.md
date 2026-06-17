# Mapeamento didático de requisitos → código (versão Python)

Este documento explica, requisito a requisito, onde no código cada funcionalidade foi implementada, como funciona passo a passo e mostra pequenos trechos de código para facilitar entendimento e apresentação.

Formato por requisito:
- Descrição curta
- Arquivos / funções envolvidas (links)
- Como funciona (passos detalhados)
- Trecho de código relevante

OBS: Para abrir os arquivos referenciados, use os caminhos do workspace (ex.: [versao Python/core.py](versao%20Python/core.py)).

---

RF01 — Importar mapas reais e converter para grafos (0.75)
- Onde: [versao Python/core.py](versao%20Python/core.py)
- Funções-chave: `carregar_grafo`, `carregar_osm_xml`, `carregar_txt`, `carregar_poly`.
- Como funciona:
  1. `carregar_grafo(caminho)` detecta extensão e escolhe o carregador adequado.
  2. Para OSM/XML, `carregar_osm_xml` usa `xml.etree.ElementTree.iterparse` (streaming) e coleta `node` e `way`.
  3. Calcula média de lat/lon para referência (`lat0, lon0`) e converte cada nó para coordenadas planas via `_projetar_latlon`.
  4. Adiciona vértices em `Grafo` (com `adicionar_vertice`) e arestas com `_adicionar_aresta`.
- Trecho (simplificado):

```python
from core import carregar_grafo
grafo = carregar_grafo('Campus2UFG&Regiao.osm')
```

E no `core.py` (processo OSM):

```python
for _, elem in ET.iterparse(caminho_arq, events=('end',)):
    tag = _tag_sem_namespace(elem.tag)
    if tag == 'node':
        nos[int(node_id)] = (float(lat), float(lon))
    if tag == 'way':
        ways.append((refs, tags))
    elem.clear()
# depois: projetar e adicionar vértices/arestas
```

Por que é didático: o código separa parsing (streaming) da construção do grafo, permitindo tratar arquivos grandes.

---

RF02 — Enumerar vértices e rotular arestas com pesos (0.20)
- Onde: [versao Python/core.py](versao%20Python/core.py)
- Funções / métodos: `Grafo.adicionar_vertice`, `_adicionar_aresta`, `_dist`.
- Como funciona:
  1. `adicionar_vertice` faz `vid = len(self.vertices)` e cria `Vertice(vid, x, y, label)`.
  2. `adicionar_aresta` ou `_adicionar_aresta` calcula `d = _dist(u, v)` (euclidiana) e insere `(v, d, directed)` em `adj[u]`.
- Trecho:

```python
def adicionar_vertice(self, x, y, label=None):
    vid = len(self.vertices)
    self.vertices.append(Vertice(vid, x, y, label))
    self.adj.append([])
    return vid

def _adicionar_aresta(grafo, u, v, directed=False):
    d = math.hypot(grafo.vertices[u].x - grafo.vertices[v].x, grafo.vertices[u].y - grafo.vertices[v].y)
    grafo.adj[u].append((v, d, directed))
```

---

RF03 — Seleção de origem/destino com desfazer e cores (0.20)
- Onde: [versao Python/main.py](versao%20Python/main.py)
- Funções-chave: `vertice_mais_proximo`, `handle_click`, `desenhar_grafo`.
- Como funciona:
  1. Usuário clica no mapa; `handle_click` chama `vertice_mais_proximo` para identificar `vid` mais próximo.
  2. Em modo `origem` ou `destino`, `self.origem` ou `self.destino` é atualizado.
  3. `desenhar_grafo` colore `origem` com `COR_ORIGEM` e `destino` com `COR_DESTINO`.
- Trecho:

```python
def vertice_mais_proximo(self, sx, sy, max_px=14):
    wx, wy = self.cam.tela_para_mundo(sx, sy)
    for v in self.grafo.vertices:
        d2 = (v.x - wx)**2 + (v.y - wy)**2
        ...
    return melhor

# no handle_click:
if self.modo == 'origem' and vid >= 0:
    self.origem = vid
```

---

RF04 — Calcular e exibir rota do menor caminho (1.50)
- Onde: [versao Python/algorithms.py](versao%20Python/algorithms.py#L1-L200) e [versao Python/main.py](versao%20Python/main.py)
- Funções-chave: `dijkstra`, `executar_dijkstra`, `desenhar_grafo`.
- Como funciona (passos):
  1. Usuário define origem/destino e clica em calcular (`executar_dijkstra`).
  2. `executar_dijkstra` chama `dijkstra(grafo, origem, destino)`.
  3. `dijkstra` usa `heapq` para extrair vértice com menor distância conhecida, relaxa arestas e mantém `prev` para reconstrução do caminho.
  4. Retorna `caminho, distancia_total, nos_explorados, tempo_ms`; `main` guarda `self.caminho` e `self.caminho_set`.
  5. `desenhar_grafo` verifica pares adjacentes do `caminho` e desenha em cor diferenciada.
- Trecho (chamada):

```python
cam, dist_total, explorados, tempo = dijkstra(self.grafo, self.origem, self.destino)
self.caminho = cam
self.caminho_set = set(cam)
```

E no `algorithms.dijkstra` (simplificado):

```python
dist = [INF]*n; dist[inicio]=0
heap=[(0.0,inicio)]
while heap:
    d,u = heapq.heappop(heap)
    if visited[u]: continue
    visited[u]=True
    if u==fim: break
    for v,w,_ in grafo.adj[u]:
        nd = d+w
        if nd < dist[v]:
            dist[v]=nd; prev[v]=u; heapq.heappush(heap,(nd,v))
```

---

RF05 — Criar/editar grafos via mouse (1.10)
- Onde: [versao Python/main.py](versao%20Python/main.py) e [versao Python/core.py](versao%20Python/core.py)
- Modos envolvidos: `add_vertice`, `add_aresta`, `add_aresta_dir`, `deletar`, `deletar_aresta`.
- Como funciona:
  1. Em modo `add_vertice`, clique converte coordenada tela→mundo com `Camera` e chama `grafo.adicionar_vertice`.
  2. Em modo `add_aresta`, primeiro clique seleciona `u`, segundo seleciona `v` e chama `grafo.adicionar_aresta(u,v,directed)`.
  3. Em `deletar` / `deletar_aresta`, `remover_vertice` / `remover_aresta` são chamados.
- Trecho:

```python
elif self.modo == 'add_vertice':
    wx, wy = self.cam.tela_para_mundo(sx, sy)
    nid = self.grafo.adicionar_vertice(wx, wy)

elif self.modo in ('add_aresta','add_aresta_dir'):
    if self.add_aresta_primeiro < 0:
        self.add_aresta_primeiro = vid
    else:
        u = self.add_aresta_primeiro
        directed = self.modo == 'add_aresta_dir'
        d = self.grafo.adicionar_aresta(u, vid, directed)
```

---

RF06 — Suporte a grafos ponderados e dirigidos (1.30)
- Onde: [versao Python/core.py](versao%20Python/core.py)
- Como funciona:
  - Cada entrada em `adj[u]` é `(v, d, directed)`; `directed` é booleano.
  - `adicionar_aresta(u,v,directed)` adiciona somente `adj[u].append((v,d,directed))` e, se não `directed`, também `adj[v].append((u,d,directed))`.
  - Carregadores interpretam flags `oneway`/`dir` e passam `directed=True` quando necessário.
- Trecho:

```python
def adicionar_aresta(self, u, v, directed=False):
    d = self._dist(u, v)
    self.adj[u].append((v, d, directed))
    if not directed:
        self.adj[v].append((u, d, directed))
```

---

RF07 — Exibir estatísticas sobre execução (0.75)
- Onde: [versao Python/algorithms.py](versao%20Python/algorithms.py#L1-L200) e [versao Python/main.py](versao%20Python/main.py)
- Como funciona:
  1. `dijkstra` mede tempo com `time.perf_counter()` e conta `explorados`.
  2. `executar_dijkstra` atribui `self.nos_explorados` e `self.tempo_ms` e atualiza sidebar via `desenhar_sidebar`.
- Trecho:

```python
t0 = time.perf_counter()
# ... execução ...
tempo_ms = (time.perf_counter() - t0) * 1000
return caminho, dist[fim], explorados, tempo_ms
```

---

RF08 — Copiar imagem do grafo para clipboard (0.20)

- Onde: [versao Python/main.py](versao%20Python/main.py) — método `copiar_imagem` e `_copiar_windows`.
- Como funciona:
  1. `copiar_imagem` captura `ultimo_grafo_surf` (Surface Pygame) e detecta o sistema operacional.
  2. **Windows**: salva a Surface como PNG em arquivo temporário via `pygame.image.save`, depois invoca PowerShell com `System.Windows.Forms.Clipboard::SetImage` — compatível com Win+V e qualquer aplicativo.
  3. **macOS**: `osascript` com `«class PNGf»`.
  4. **Linux/Docker**: `xclip -selection clipboard -t image/png`.
  5. Se qualquer etapa falhar, salva `grafo_<numero>.png` no diretório atual (fallback).
- Trecho (Windows):

```python
ps = (
    'Add-Type -AssemblyName System.Windows.Forms; '
    'Add-Type -AssemblyName System.Drawing; '
    f'$img = [System.Drawing.Image]::FromFile("{tmp_ps}"); '
    '[System.Windows.Forms.Clipboard]::SetImage($img); '
    '$img.Dispose()'
)
subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps], ...)
```

---

RNF01 — Cores distintas para vértices/arestas (0.25)
- Onde: [versao Python/gui.py](versao%20Python/gui.py) e [versao Python/main.py](versao%20Python/main.py)
- Como: constantes `COR_VERTICE`, `COR_ARESTA`, `COR_CAMINHO_V`, etc.; aplicadas em `desenhar_grafo`.

RNF02 — Diferenciar mão-única / mão-dupla (0.25)
- Onde: [versao Python/core.py](versao%20Python/core.py) e [versao Python/main.py](versao%20Python/main.py)
- Como: `directed` flag e desenho de setas quando `directed=True`.

RNF03 — Otimização para grandes grafos (0.25)
- Onde: parsing streaming em [versao Python/core.py](versao%20Python/core.py)
- Observação: principal otimização atual é streaming e uso de listas de adjacência; recomenda-se integrar R-tree para buscas interativas.

RNF04 — Tempo de resposta < 2s para grafos médios (0.25)
- Onde: `algorithms.dijkstra` — complexidade O((V+E) log V)
- Observação: medir localmente com script de benchmark; A* pode reduzir nós explorados.

RNF05 — Uso eficiente de memória (0.25)
- Onde: `Vertice.__slots__` em [versao Python/core.py](versao%20Python/core.py)

RNF06 — Interface intuitiva (0.25)
- Onde: `main.py` e `gui.py` — botões, atalhos, mensagens de log.

RNF07 — Suporte Windows/Linux (0.25)
- Onde: código Python + Pygame é multiplataforma; clipboard Windows-specific em `main.copiar_imagem`.

RNF08 — Código modular e bem documentado (0.25)
- Onde: estrutura em módulos (`core`, `algorithms`, `gui`, `main`) e documentação adicionada em `DOCUMENTATION.md` e `SOFTWARE_ENGINEERING.md`.

---
