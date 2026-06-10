"""
Algoritmos puros do sistema de navegação.

1. Para que serve o arquivo:
     - Contém implementações dos algoritmos de grafo usados pela aplicação (atual
         e futuros), separados da interface gráfica e da modelagem de dados.

2. Como funciona (resumo):
     - Atualmente fornece `dijkstra(grafo, inicio, fim)` que calcula o menor
         caminho em grafos ponderados, usando `heapq` (fila de prioridade).
     - Mede tempo de execução e número de nós explorados, retornando esses
         metadados para exibição na interface.

3. Quais requisitos atende:
     - RF04: Calcular e exibir rota do menor caminho — `dijkstra` devolve
         caminho, distância, nós explorados e tempo (ms).
     - RNF04: Eficiência/complexidade — implementação baseada em heap: O((V+E) log V).

Notas de manutenção:
     - Funções adicionais (A*, Bellman-Ford) podem ser colocadas aqui para
         facilitar comparação/benchmark.
"""

import heapq
import time


def dijkstra(grafo, inicio, fim):
    """Retorna (caminho, distancia_total, nos_explorados, tempo_ms)."""
    INF = float('inf')
    n = len(grafo.vertices)
    dist = [INF] * n
    prev = [-1] * n
    visited = [False] * n

    dist[inicio] = 0.0
    heap = [(0.0, inicio)]
    explorados = 0
    t0 = time.perf_counter()

    while heap:
        d, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        explorados += 1

        if u == fim:
            break

        for (v, w, _) in grafo.adj[u]:
            if grafo.vertices[v] is None or visited[v]:
                continue
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    tempo_ms = (time.perf_counter() - t0) * 1000

    if dist[fim] == INF:
        return [], INF, explorados, tempo_ms

    caminho = []
    v = fim
    while v != -1:
        caminho.append(v)
        v = prev[v]
    caminho.reverse()

    return caminho, dist[fim], explorados, tempo_ms