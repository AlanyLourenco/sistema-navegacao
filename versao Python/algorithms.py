"""
Algoritmos puros do sistema de navegacao.
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