# Conceitos de AED2 Aplicados no Projeto

> **Arquivo:** `01_conceitos_aed2.md`  
> **Relacionado a:** todos os módulos (`core.py`, `algorithms.py`, `gui.py`, `main.py`)

Este documento mapeia explicitamente cada conteúdo teórico da disciplina de **Algoritmos e Estruturas de Dados 2** para a implementação concreta no NavGrafo UFG.

---

## 1. Grafos Ponderados e Dirigidos

**Onde aparece na teoria:** Definição formal de grafos G = (V, E), tipos de arestas, pesos.

**Como está implementado:**

O grafo do sistema é **ponderado** — cada aresta tem um peso real correspondente à distância euclidiana entre os dois vértices (em metros, após projeção geográfica). O grafo também suporta dois tipos de arestas:

- **Não-dirigidas** (`directed=False`): representam vias de mão dupla. A inserção na lista de adjacência é feita nos dois sentidos.
- **Dirigidas** (`directed=True`): representam vias de mão única (`oneway` em mapas OSM). Inseridas em apenas um sentido.

```python
# core.py — Grafo.adicionar_aresta
def adicionar_aresta(self, u, v, directed=False):
    d = self._dist(u, v)
    self.adj[u].append((v, d, directed))
    if not directed:
        self.adj[v].append((u, d, directed))   # ← sentido reverso só se bidirecional
```

**Relevância para AED2:** A distinção entre grafos dirigidos e não-dirigidos impacta diretamente a execução do Dijkstra — em um grafo dirigido, a existência de caminho de `u` para `v` não implica caminho de `v` para `u`.

---

## 2. Lista de Adjacência

**Onde aparece na teoria:** Representações de grafos — Matriz de adjacência vs. Lista de adjacência.

**Como está implementado:**

```python
# core.py — Grafo
self.adj = []   # adj[u] = [(v, peso, directed), ...]
```

Cada posição `adj[u]` é uma lista Python contendo apenas os vizinhos diretos de `u`, com o respectivo peso da aresta e o flag de direção.

**Por que lista e não matriz?**

| | Matriz de Adjacência | Lista de Adjacência |
|---|---|---|
| Memória | `O(V²)` — 100M entradas para V=10k | `O(V + E)` — ~21.5k entradas |
| Iterar vizinhos | `O(V)` | `O(grau(v))` |
| Verificar aresta | `O(1)` | `O(grau(v))` |
| **Indicado para** | Grafos densos | **Grafos esparsos** ← mapas viários |

O grafo do Campus UFG tem `E ≈ 11.526` para `V ≈ 10.000`, ou seja, `E << V²`. A lista de adjacência é a escolha correta e é amplamente mais eficiente em memória neste cenário.

---

## 3. Fila de Prioridade (Min-Heap)

**Onde aparece na teoria:** Filas de prioridade, Heap binário, operações `insert` e `extract-min`.

**Como está implementado:**

O Dijkstra usa o módulo `heapq` do Python, que implementa um **heap mínimo binário** sobre uma lista comum:

```python
# algorithms.py
import heapq

heap = [(0.0, inicio)]          # (distância_provisória, vértice)

d, u = heapq.heappop(heap)      # extract-min — O(log n)
heapq.heappush(heap, (nd, v))   # insert     — O(log n)
```

**Por que isso é fundamental?**

Sem heap, o Dijkstra precisaria varrer todos os vértices para encontrar o de menor distância a cada iteração — custo `O(V)` por extração, totalizando `O(V²)` para o algoritmo inteiro. Com o heap, cada extração custa `O(log V)`, reduzindo o total para `O((V + E) log V)`.

Para V = 10.000: a diferença é de **100 milhões** de operações (sem heap) vs. **~143 mil** (com heap).

---

## 4. Análise de Complexidade Assintótica

**Onde aparece na teoria:** Notação O, Ω, Θ; análise de pior caso, caso médio.

**Como está aplicado:**

Cada módulo foi desenvolvido com atenção à complexidade das operações críticas:

| Operação | Complexidade | Módulo |
|---|---|---|
| `dijkstra` (com heap) | `O((V + E) log V)` | `algorithms.py` |
| `adicionar_aresta` | `O(1)` amortizado | `core.py` |
| `remover_vertice` | `O(V + E)` | `core.py` |
| `vertice_mais_proximo` | `O(V)` | `main.py` |
| `aresta_mais_proxima` | `O(E)` | `main.py` |
| `carregar_osm_xml` (streaming) | `O(V + E)` | `core.py` |
| `cam.fit` | `O(V)` | `gui.py` |

> **Nota de melhoria identificada no código:** `vertice_mais_proximo` e `aresta_mais_proxima` são O(V) e O(E) e varridos a cada clique do usuário. Para grafos com centenas de milhares de nós, uma **R-tree** (árvore de busca espacial) reduziria isso para `O(log V)`.

---

## 5. Gerenciamento de Memória com `__slots__`

**Onde aparece na teoria:** Estruturas de dados eficientes, overhead de objetos.

**Como está implementado:**

```python
# core.py
class Vertice:
    __slots__ = ('id', 'x', 'y', 'label')
```

Em Python, cada objeto normalmente possui um dicionário interno `__dict__` para armazenar seus atributos, consumindo entre 200–400 bytes extras por instância. O `__slots__` substitui esse dicionário por campos de tamanho fixo, economizando aproximadamente **4–6 MB** ao instanciar 10.000 vértices.

---

## 6. Parsing com Processamento em Fluxo (Streaming)

**Onde aparece na teoria:** Estruturas de dados externas, acesso a arquivos grandes, processamento sequencial.

**Como está implementado:**

```python
# core.py — carregar_osm_xml
for _, elem in ET.iterparse(caminho_arq, events=('end',)):
    # processa elem
    elem.clear()   # ← libera memória imediatamente após uso
```

O `iterparse` processa o XML elemento por elemento, sem carregar o arquivo inteiro na RAM. O `elem.clear()` libera a árvore de cada elemento já processado. Para arquivos OSM de cidades inteiras (que podem ter centenas de MB), essa técnica é indispensável.

---

## 7. Reconstrução de Caminho com Array de Predecessores

**Onde aparece na teoria:** Árvore de caminhos mínimos, predecessor `π[v]`.

**Como está implementado:**

```python
# algorithms.py
prev = [-1] * n          # prev[v] = antecessor de v no caminho mínimo

# Durante o Dijkstra:
if nd < dist[v]:
    prev[v] = u          # registra de onde viemos para chegar em v

# Reconstrução após encontrar o destino:
caminho = []
v = fim
while v != -1:
    caminho.append(v)
    v = prev[v]          # percorre de trás para frente
caminho.reverse()
```

O array `prev` implementa a **árvore de caminhos mínimos** do Dijkstra. Percorrê-lo de `fim` até `inicio` (onde `prev[inicio] == -1`) reconstrói o caminho em `O(|caminho|)`.

---

## Resumo: Conteúdo de AED2 × Módulo

| Conteúdo AED2 | Módulo | Elemento específico |
|---|---|---|
| Grafos ponderados e dirigidos | `core.py` | `Grafo`, `adicionar_aresta` |
| Lista de adjacência | `core.py` | `Grafo.adj` |
| Fila de prioridade / Min-Heap | `algorithms.py` | `heapq` no Dijkstra |
| Dijkstra — caminho mínimo | `algorithms.py` | `dijkstra()` |
| Análise assintótica | todos | comentários, docstrings |
| `__slots__` / memória eficiente | `core.py` | `Vertice.__slots__` |
| Streaming de arquivos grandes | `core.py` | `iterparse` + `elem.clear()` |
| Array de predecessores π | `algorithms.py` | `prev[]` e reconstrução |
| Relaxamento de arestas | `algorithms.py` | `if nd < dist[v]` |