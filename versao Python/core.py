"""
Estruturas centrais do sistema de navegação em grafos.

Este módulo nao importa pygame e concentra apenas logica de dados e leitura
de arquivos .poly, .txt estruturado e mapas OSM/XML.
"""

import math
import os
import xml.etree.ElementTree as ET


class Vertice:
    __slots__ = ('id', 'x', 'y', 'label')

    def __init__(self, id, x, y, label=None):
        self.id = id
        self.x = x
        self.y = y
        self.label = label if label is not None else id


class Grafo:
    """Grafo com lista de adjacencia e suporte a arestas dirigidas e nao dirigidas."""

    def __init__(self):
        self.vertices = []
        self.adj = []
        self.arestas_raw = []

    def adicionar_vertice(self, x, y, label=None):
        vid = len(self.vertices)
        self.vertices.append(Vertice(vid, x, y, label))
        self.adj.append([])
        return vid

    def adicionar_aresta(self, u, v, directed=False):
        d = self._dist(u, v)
        self.adj[u].append((v, d, directed))
        if not directed:
            self.adj[v].append((u, d, directed))
        self.arestas_raw.append((u, v, directed))
        return d

    def remover_aresta(self, u, v, directed=None):
        """Remove a primeira aresta que ligue u e v.

        Se directed for None, remove a primeira ligação encontrada entre os dois
        vértices, seja dirigida ou não. Se directed for True/False, exige o
        sentido correspondente.
        """
        for idx, (a, b, dr) in enumerate(self.arestas_raw):
            if directed is not None and dr != directed:
                continue
            if dr:
                match = (a == u and b == v) or (directed is None and a == v and b == u)
            else:
                match = {a, b} == {u, v}
            if not match:
                continue

            self.arestas_raw.pop(idx)

            def filtrar(lista, origem, destino, d_ind):
                nova = []
                removido = False
                for item in lista:
                    j, d, dr_item = item
                    if not removido and j == destino and dr_item == d_ind:
                        removido = True
                        continue
                    nova.append(item)
                return nova

            self.adj[a] = filtrar(self.adj[a], a, b, dr)
            if not dr:
                self.adj[b] = filtrar(self.adj[b], b, a, dr)
            elif directed is None and a == v and b == u:
                self.adj[b] = filtrar(self.adj[b], b, a, dr)

            return True

        return False

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


def _adicionar_aresta(grafo, u, v, directed=False):
    d = math.hypot(
        grafo.vertices[u].x - grafo.vertices[v].x,
        grafo.vertices[u].y - grafo.vertices[v].y,
    )
    grafo.adj[u].append((v, d, directed))
    if not directed:
        grafo.adj[v].append((u, d, directed))
    grafo.arestas_raw.append((u, v, directed))


def _limpar_linha_texto(linha):
    linha = linha.split('#', 1)[0]
    linha = linha.split('//', 1)[0]
    linha = linha.split(';', 1)[0]
    return linha.strip()


def _eh_rotulo_seccao(texto, opcoes):
    texto = texto.strip().lower().rstrip(':').strip()
    return texto in opcoes


def carregar_txt(caminho_arq):
    """Carrega um mapa em texto estruturado com seções VERTICES e ARESTAS."""
    grafo = Grafo()
    vertices_externos = []
    arestas_externas = []

    secao = None
    with open(caminho_arq, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = _limpar_linha_texto(linha)
            if not linha:
                continue

            if _eh_rotulo_seccao(linha, {'vertices', 'vertex', 'nodes', 'nodos'}):
                secao = 'vertices'
                continue
            if _eh_rotulo_seccao(linha, {'arestas', 'arestas dir', 'edges', 'arcos', 'links'}):
                secao = 'arestas'
                continue

            partes = [p for p in linha.replace(',', ' ').split() if p]
            if secao == 'vertices':
                if len(partes) < 3:
                    raise ValueError('Linha de vértice inválida no TXT estruturado')
                ext_id = int(partes[0])
                x = float(partes[1])
                y = float(partes[2])
                rotulo = ' '.join(partes[3:]) if len(partes) > 3 else ext_id
                vertices_externos.append((ext_id, x, y, rotulo))
                continue

            if secao == 'arestas':
                if len(partes) < 2:
                    raise ValueError('Linha de aresta inválida no TXT estruturado')
                u = int(partes[0])
                v = int(partes[1])
                directed = False
                if len(partes) >= 3:
                    flag = partes[2].lower()
                    directed = flag in {'1', 'd', 'dir', 'direta', 'directed', 'oneway', '->'}
                arestas_externas.append((u, v, directed))
                continue

            raise ValueError('Arquivo TXT precisa ter seções VERTICES e ARESTAS')

    if not vertices_externos:
        raise ValueError('Nenhum vértice encontrado no TXT')

    mapa_ids = {}
    for ext_id, x, y, rotulo in vertices_externos:
        mapa_ids[ext_id] = grafo.adicionar_vertice(x, y, rotulo)

    for u_ext, v_ext, directed in arestas_externas:
        if u_ext not in mapa_ids or v_ext not in mapa_ids:
            continue
        _adicionar_aresta(grafo, mapa_ids[u_ext], mapa_ids[v_ext], directed)

    return grafo


def _tag_sem_namespace(tag):
    return tag.rsplit('}', 1)[-1]


def _projetar_latlon(lat, lon, lat0, lon0):
    raio = 6371000.0
    rad = math.pi / 180.0
    x = (lon - lon0) * rad * math.cos(lat0 * rad) * raio
    y = -(lat - lat0) * rad * raio
    return x, y


def carregar_osm_xml(caminho_arq):
    """Carrega um mapa OSM/XML e converte vias para um grafo."""
    nos = {}
    ways = []

    for _, elem in ET.iterparse(caminho_arq, events=('end',)):
        tag = _tag_sem_namespace(elem.tag)

        if tag == 'node':
            node_id = elem.attrib.get('id')
            lat = elem.attrib.get('lat')
            lon = elem.attrib.get('lon')
            if node_id is not None and lat is not None and lon is not None:
                nos[int(node_id)] = (float(lat), float(lon))
            elem.clear()
            continue

        if tag == 'way':
            refs = []
            tags = {}
            for child in list(elem):
                child_tag = _tag_sem_namespace(child.tag)
                if child_tag == 'nd':
                    ref = child.attrib.get('ref')
                    if ref is not None:
                        refs.append(int(ref))
                elif child_tag == 'tag':
                    chave = child.attrib.get('k')
                    valor = child.attrib.get('v', '')
                    if chave:
                        tags[chave] = valor

            if refs:
                ways.append((refs, tags))
            elem.clear()

    ways_filtradas = [item for item in ways if 'highway' in item[1]]
    if not ways_filtradas:
        ways_filtradas = ways

    ids_usados = []
    for refs, _ in ways_filtradas:
        for ref in refs:
            if ref in nos:
                ids_usados.append(ref)

    if not ids_usados:
        raise ValueError('Nenhum nó OSM válido foi encontrado')

    lat0 = sum(nos[node_id][0] for node_id in ids_usados) / len(ids_usados)
    lon0 = sum(nos[node_id][1] for node_id in ids_usados) / len(ids_usados)

    grafo = Grafo()
    mapa_ids = {}
    for node_id in ids_usados:
        if node_id in mapa_ids:
            continue
        lat, lon = nos[node_id]
        x, y = _projetar_latlon(lat, lon, lat0, lon0)
        mapa_ids[node_id] = grafo.adicionar_vertice(x, y, node_id)

    for refs, tags in ways_filtradas:
        oneway = tags.get('oneway', '').strip().lower()
        directed = oneway in {'yes', 'true', '1', '-1'}
        seq = [mapa_ids[ref] for ref in refs if ref in mapa_ids]
        if oneway == '-1':
            seq.reverse()
        for i in range(len(seq) - 1):
            _adicionar_aresta(grafo, seq[i], seq[i + 1], directed)

    return grafo


def carregar_grafo(caminho_arq):
    """Seleciona automaticamente o carregador pelo tipo de arquivo."""
    ext = os.path.splitext(caminho_arq)[1].lower()

    if ext == '.poly':
        return carregar_poly(caminho_arq)
    if ext in {'.osm', '.xml', '.xlml'}:
        return carregar_osm_xml(caminho_arq)
    if ext in {'.txt', '.csv', '.tsv', '.dat'}:
        return carregar_txt(caminho_arq)

    with open(caminho_arq, 'r', encoding='utf-8') as f:
        inicio = f.read(256).lstrip()

    if inicio.startswith('<'):
        return carregar_osm_xml(caminho_arq)

    return carregar_txt(caminho_arq)