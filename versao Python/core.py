"""
Estruturas centrais do sistema de navegação em grafos.

Este módulo nao importa pygame e concentra apenas logica de dados e leitura
do arquivo .poly.
"""

import math


class Vertice:
    __slots__ = ('id', 'x', 'y')

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class Grafo:
    """Grafo com lista de adjacencia e suporte a arestas dirigidas e nao dirigidas."""

    def __init__(self):
        self.vertices = []
        self.adj = []
        self.arestas_raw = []

    def adicionar_vertice(self, x, y):
        vid = len(self.vertices)
        self.vertices.append(Vertice(vid, x, y))
        self.adj.append([])
        return vid

    def adicionar_aresta(self, u, v, directed=False):
        d = self._dist(u, v)
        self.adj[u].append((v, d, directed))
        if not directed:
            self.adj[v].append((u, d, directed))
        self.arestas_raw.append((u, v, directed))
        return d

    def remover_vertice(self, vid):
        self.vertices[vid] = None
        self.adj[vid] = []
        for i in range(len(self.adj)):
            if self.adj[i]:
                self.adj[i] = [(j, d, dr) for (j, d, dr) in self.adj[i] if j != vid]
        self.arestas_raw = [(u, v, dr) for (u, v, dr) in self.arestas_raw if u != vid and v != vid]

    def _dist(self, u, v):
        vu, vv = self.vertices[u], self.vertices[v]
        return math.hypot(vu.x - vv.x, vu.y - vv.y)

    @property
    def total_vertices(self):
        return sum(1 for v in self.vertices if v is not None)

    @property
    def total_arestas(self):
        return len(self.arestas_raw)


def carregar_poly(caminho_arq):
    """Carrega um arquivo .poly para uma instancia de Grafo."""
    grafo = Grafo()
    with open(caminho_arq, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    idx = 0
    partes = linhas[idx].split()
    n_v = int(partes[0])
    idx += 1

    for _ in range(n_v):
        p = linhas[idx].split()
        grafo.vertices.append(Vertice(int(p[0]), float(p[1]), float(p[2])))
        grafo.adj.append([])
        idx += 1

    partes = linhas[idx].split()
    n_e = int(partes[0])
    idx += 1

    for _ in range(n_e):
        p = linhas[idx].split()
        u = int(p[1])
        v = int(p[2])
        dir_flag = int(p[3])
        directed = (dir_flag == 1)
        d = math.hypot(
            grafo.vertices[u].x - grafo.vertices[v].x,
            grafo.vertices[u].y - grafo.vertices[v].y,
        )
        grafo.adj[u].append((v, d, directed))
        if not directed:
            grafo.adj[v].append((u, d, directed))
        grafo.arestas_raw.append((u, v, directed))
        idx += 1

    return grafo