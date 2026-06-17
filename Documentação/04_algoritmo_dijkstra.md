# Algoritmo de Dijkstra

> **Arquivo:** `04_algoritmo_dijkstra.md`  
> **Módulo:** `algorithms.py`

---

## O que resolve

O Dijkstra resolve o problema do **caminho mínimo de fonte única** em grafos com pesos não-negativos. Dado um vértice de origem, ele encontra o menor caminho (menor soma de pesos) até qualquer outro vértice alcançável.

No NavGrafo UFG, é invocado para encontrar a rota mais curta entre dois pontos selecionados pelo usuário no mapa.

> **Restrição importante:** o Dijkstra não funciona corretamente com arestas de peso negativo. Para esse caso, seria necessário Bellman-Ford (`O(VE)`). No domínio de mapas viários, pesos negativos não fazem sentido físico, então Dijkstra é a escolha correta.

---

## Implementação completa

```python
# algorithms.py
import heapq
import time


def dijkstra(grafo, inicio, fim):
    """Retorna (caminho, distancia_total, nos_explorados, tempo_ms)."""
    INF = float('inf')
    n = len(grafo.vertices)
    dist = [INF] * n       # distâncias provisórias — todas infinito no início
    prev = [-1] * n        # predecessores — -1 = sem predecessor
    visited = [False] * n  # controle de vértices definitivamente resolvidos

    dist[inicio] = 0.0
    heap = [(0.0, inicio)]  # min-heap: (distância_provisória, vértice)
    explorados = 0
    t0 = time.perf_counter()

    while heap:
        d, u = heapq.heappop(heap)   # extrai vértice com menor distância — O(log n)

        if visited[u]:
            continue   # descarta entradas obsoletas do heap (lazy deletion)

        visited[u] = True
        explorados += 1

        if u == fim:
            break      # early exit — destino encontrado, não precisa continuar

        for (v, w, _) in grafo.adj[u]:           # percorre vizinhos de u
            if grafo.vertices[v] is None or visited[v]:
                continue
            nd = d + w                           # distância candidata até v passando por u
            if nd < dist[v]:                     # relaxamento da aresta (u, v)
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))    # insere no heap — O(log n)

    tempo_ms = (time.perf_counter() - t0) * 1000

    if dist[fim] == INF:
        return [], INF, explorados, tempo_ms     # destino inacessível

    # Reconstrução do caminho percorrendo prev[] de fim → inicio
    caminho = []
    v = fim
    while v != -1:
        caminho.append(v)
        v = prev[v]
    caminho.reverse()

    return caminho, dist[fim], explorados, tempo_ms
```

---

## Fluxograma detalhado

```mermaid
flowchart TD
    I([Início]) --> INIT["dist[todos] = ∞\ndist[origem] = 0\nprev[todos] = -1\nheap = [(0.0, origem)]"]
    INIT --> LOOP{heap\nvazio?}

    LOOP -->|Sim| NOWAY["dist[fim] == ∞ ?\nCaminho inexistente"]
    NOWAY --> RET_VAZIO([Retorna [], ∞, explorados, ms])

    LOOP -->|Não| POP["(d, u) = heappop(heap)\nextrai mínimo — O(log n)"]
    POP --> VIS{visited[u]?}
    VIS -->|Sim — entrada obsoleta| LOOP
    VIS -->|Não| MARK["visited[u] = True\nexplorados += 1"]

    MARK --> FIM{u == destino?}
    FIM -->|Sim — early exit| RECON

    FIM -->|Não| ADJ["Para cada (v, w, _)\nem grafo.adj[u]:"]
    ADJ --> SKIP{"vertices[v] == None\nou visited[v]?"}
    SKIP -->|Sim| PROX[próximo vizinho]
    PROX --> ADJ

    SKIP -->|Não| REL["nd = d + w\n(distância candidata)"]
    REL --> BETTER{nd < dist[v]?}
    BETTER -->|Não| PROX
    BETTER -->|Sim — relaxamento| UPD["dist[v] = nd\nprev[v] = u\nheappush(heap, (nd, v))"]
    UPD --> PROX

    RECON["Reconstrução:\nv = fim\nwhile v != -1:\n  caminho.append(v)\n  v = prev[v]\ncaminho.reverse()"]
    RECON --> RET([Retorna caminho,\ndist[fim], explorados, ms])

    style I fill:#1a3a2a,color:#74d48a
    style RET fill:#1a3a2a,color:#74d48a
    style RET_VAZIO fill:#3a1a1a,color:#d45a4a
    style NOWAY fill:#3a1a1a,color:#d45a4a
```

---

## Exemplo passo a passo

Grafo de 4 vértices: A(0)→B(1)→C(2)→D(3), com atalho A→C.

```
         2.0          1.0
    A ──────── B ──────── D
    │                     ▲
    │   5.0               │
    └──────── C ──────────┘
                   1.5
```

**Executando `dijkstra(grafo, 0, 3)`:**

| Iteração | Heap (min) | u extraído | dist[] atualizado | visited |
|---|---|---|---|---|
| 0 (init) | `[(0, A)]` | — | `[0, ∞, ∞, ∞]` | `{}` |
| 1 | `[(2,B),(5,C)]` | A | `[0, 2, 5, ∞]` | `{A}` |
| 2 | `[(3,D),(5,C)]` | B | `[0, 2, 5, 3]` | `{A,B}` |
| 3 | `[(4.5,D),(5,C)]`| D? | early exit! | `{A,B,D}` |

**Reconstrução via `prev`:** prev = [-1, 0, 0, 1] → D←B←A → caminho: [A, B, D]  
**Distância:** 3.0 (A→B=2.0 + B→D=1.0, mais curto que A→C→D=5.0+1.5=6.5)

---

## Lazy deletion no heap

O Dijkstra implementado usa **lazy deletion**: quando a distância de um vértice é atualizada, o heap pode conter entradas antigas para o mesmo vértice. Em vez de remover a entrada antiga (operação cara no heap), simplesmente ignoramos quando encontramos um vértice já visitado:

```python
d, u = heapq.heappop(heap)
if visited[u]:
    continue    # ← lazy deletion: descarta entrada obsoleta
```

Essa técnica é o padrão em implementações de produção com `heapq`, pois `heapq` do Python não suporta `decrease-key` diretamente.

---

## Early exit

```python
if u == fim:
    break
```

Quando o vértice extraído do heap é o destino, ele já tem a distância mínima garantida (propriedade do Dijkstra). Não é necessário continuar expandindo os demais vértices — o que pode economizar muitas iterações quando origem e destino estão próximos.

---

## Retorno da função

```python
return caminho, dist[fim], explorados, tempo_ms
```

| Campo | Tipo | Descrição |
|---|---|---|
| `caminho` | `list[int]` | Sequência de IDs de vértices da origem ao destino |
| `dist[fim]` | `float` | Distância total em metros |
| `explorados` | `int` | Número de vértices processados (≤ V) |
| `tempo_ms` | `float` | Tempo de execução em milissegundos |

Todos os quatro valores são exibidos no painel lateral da interface ao calcular uma rota.

---

## Integração com `main.py`

```python
# main.py — App.executar_dijkstra
def executar_dijkstra(self):
    if self.origem < 0 or self.destino < 0:
        self.log('Selecione origem e destino primeiro.', 'warn')
        return

    caminho, dist, explorados, ms = dijkstra(self.grafo, self.origem, self.destino)

    if not caminho:
        self.log('Sem caminho entre os vértices selecionados.', 'err')
        return

    self.caminho = caminho
    self.caminho_set = set(zip(caminho, caminho[1:]))  # pares (u,v) para colorir arestas
    self.caminho_dist = dist
    self.nos_explorados = explorados
    self.tempo_ms = ms
    self.log(f'Rota: {len(caminho)} vértices | {dist:.1f}m | {ms:.2f}ms', 'ok')
```