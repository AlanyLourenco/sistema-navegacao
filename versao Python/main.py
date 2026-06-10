"""
Aplicação principal do sistema de navegação em grafos com Pygame.

1. Para que serve o arquivo:
     - Orquestra a interface gráfica (Pygame), entrada do usuário, desenho do
         grafo, modos de edição e integrações com os módulos `core` e `algorithms`.

2. Como funciona (resumo):
     - Inicializa a janela, fontes, botões e a `Camera` e mantém o estado da
         aplicação (`grafo`, `origem`, `destino`, `caminho`, modos de edição).
     - Fornece handlers: `handle_click`, `handle_botao`, `pedir_arquivo`, e o
         laço principal `run()` que processa eventos, teclas e desenha a tela.
     - Implementa seleção por clique (`vertice_mais_proximo`), busca da aresta
         mais próxima (`aresta_mais_proxima`), execução de Dijkstra
         (`executar_dijkstra`) e exportação para clipboard (`copiar_imagem`).

3. Quais requisitos atende:
     - RF03: Seleção de origem/destino com feedback visual e desfazer.
     - RF04: Chamadas para `dijkstra` e exibição de resultados/estatísticas.
     - RF05: Modo de edição para adicionar/remover vértices e arestas via mouse.
     - RF07: Exibição de estatísticas (nós explorados, tempo) no painel lateral.
     - RNF07: Multiplataforma (Pygame); contém fallback para clipboard em caso de
         indisponibilidade no Windows (salva PNG).

Notas de manutenção:
     - `copiar_imagem` faz manipulação nativa do clipboard via `ctypes` (Windows).
     - `vertice_mais_proximo` e `aresta_mais_proxima` são implementações O(V)/O(E)
         e podem ser aceleradas com uma estrutura espacial (R-tree) para grafos grandes.
"""

import math
import os
import sys
import time
import ctypes

import pygame

from algorithms import dijkstra
from core import carregar_grafo
from gui import (
    ALTURA,
    COR_ARESTA,
    COR_ARESTA_DIR,
    COR_BORDA,
    COR_BTN,
    COR_BTN_ATIVO,
    COR_BTN_HOVER,
    COR_CAMINHO_A,
    COR_CAMINHO_V,
    COR_DESTINO,
    COR_FUNDO,
    COR_ORIGEM,
    COR_PAINEL,
    COR_SIDEBAR,
    COR_TEXTO,
    COR_TEXTO_DIM,
    COR_TEXTO_ERR,
    COR_TEXTO_INFO,
    COR_TEXTO_OK,
    COR_TEXTO_WARN,
    COR_VERTICE,
    FPS,
    LARGURA,
    SIDEBAR_W,
    Botao,
    Camera,
)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('NavGrafo UFG — AED2 2026-1')
        self.screen = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.fonte_sm = pygame.font.SysFont('monospace', 11)
        self.fonte_md = pygame.font.SysFont('monospace', 13)
        self.fonte_lg = pygame.font.SysFont('monospace', 15, bold=True)
        self.fonte_xl = pygame.font.SysFont('monospace', 18, bold=True)
        # Fonte usada para estatísticas e logs na sidebar (um pouco maior)
        self.fonte_log = pygame.font.SysFont('monospace', 14)
        # Scroll offset para logs da sidebar (0 = fim / mais recentes)
        self.log_scroll = 0

        self.grafo = None
        self.cam = Camera()

        self.origem = -1
        self.destino = -1
        self.caminho = []
        self.caminho_set = set()
        self.caminho_dist = 0.0
        self.nos_explorados = 0
        self.tempo_ms = 0.0

        self.MODOS = ['origem', 'destino', 'add_vertice', 'add_aresta', 'add_aresta_dir', 'deletar', 'pan']
        self.MODOS = ['origem', 'destino', 'add_vertice', 'add_aresta', 'add_aresta_dir', 'deletar', 'deletar_aresta', 'pan']
        self.modo = 'origem'
        self.add_aresta_primeiro = -1

        self.pan_ativo = False
        self.pan_start = (0, 0)
        self.cam_start = (0, 0)

        self.mostrar_ids = False
        self.mostrar_pesos = False
        self.tam_vertice = 1.5
        self.esp_aresta = 0.5

        self.log_msgs = []
        self.arq_carregado = ''
        self.ultimo_grafo_surf = None

        self._criar_botoes()

    def _criar_botoes(self):
        self.botoes = {}
        self._layout_botoes()

    def _layout_botoes(self):
        sx, bw, bh, gap = 8, SIDEBAR_W - 16, 24, 6
        # Iniciar os botões mais abaixo para dar espaço ao cabeçalho maior
        y = 84

        def B(nome, txt, cor=None, ativo=False):
            nonlocal y
            b = Botao(sx, y, bw, bh, txt, cor, ativo)
            self.botoes[nome] = b
            y += bh + gap
            return b

        def SEP():
            nonlocal y
            y += 4

        B('ler_poly', '[L] Importar mapa', COR_TEXTO_INFO)
        SEP()
        B('modo_orig', '[O] Selec. Origem', COR_TEXTO_OK, self.modo == 'origem')
        B('modo_dest', '[D] Selec. Destino', COR_TEXTO_ERR, self.modo == 'destino')
        B('dijkstra', '[C] Calcular Rota', COR_TEXTO_OK)
        SEP()
        B('modo_addv', '[V] + Vértice', COR_TEXTO_INFO, self.modo == 'add_vertice')
        B('modo_adde', '[A] + Aresta (dupla)', COR_TEXTO_INFO, self.modo == 'add_aresta')
        B('modo_addd', '[U] + Aresta (única)', COR_TEXTO_WARN, self.modo == 'add_aresta_dir')
        B('modo_del', '[X] Deletar Vértice', COR_TEXTO_ERR, self.modo == 'deletar')
        B('modo_dela', '[Z] Deletar Aresta', COR_TEXTO_ERR, self.modo == 'deletar_aresta')
        B('modo_pan', '[P] Pan (mover mapa)', COR_TEXTO_DIM, self.modo == 'pan')
        SEP()
        B('limpar', '[R] Limpar Seleção', COR_TEXTO_WARN)
        B('fit', '[F] Ajustar ao Mapa', COR_TEXTO_DIM)
        SEP()
        B('tog_ids', f'[N] IDs: {"ON" if self.mostrar_ids else "off"}', COR_TEXTO_DIM, self.mostrar_ids)
        B('tog_pesos', f'[W] Pesos: {"ON" if self.mostrar_pesos else "off"}', COR_TEXTO_DIM, self.mostrar_pesos)
        SEP()
        B('copiar', '[I] Copiar Imagem', COR_TEXTO_DIM)
        B('sair', '[Q] Sair', COR_TEXTO_ERR)

        self._y_stats = y + 8
        # Ajuste: começar a área de logs mais cedo (menor offset) para aumentar espaço
        self._y_log = self._y_stats + 80

    def log(self, msg, tipo='info'):
        cores = {'info': COR_TEXTO_INFO, 'ok': COR_TEXTO_OK, 'warn': COR_TEXTO_WARN, 'err': COR_TEXTO_ERR}
        self.log_msgs.append((msg, cores.get(tipo, COR_TEXTO)))
        # Ao adicionar nova mensagem, reposicionar para o fim (auto-scroll)
        self.log_scroll = 0
        if len(self.log_msgs) > 60:
            self.log_msgs.pop(0)

    def set_modo(self, m):
        self.modo = m
        self.add_aresta_primeiro = -1
        self._layout_botoes()

    def area_grafo(self):
        W, H = self.screen.get_size()
        return pygame.Rect(SIDEBAR_W, 0, W - SIDEBAR_W, H)

    def carregar_arquivo(self, caminho):
        try:
            self.grafo = carregar_grafo(caminho)
            self.cam.fit(self.grafo.vertices, self.area_grafo().width, self.area_grafo().height)
            self.cam.x += SIDEBAR_W
            self.origem = self.destino = -1
            self.caminho = []
            self.caminho_set = set()
            self.arq_carregado = os.path.basename(caminho)
            self.log(f'Carregado: {self.arq_carregado}', 'ok')
            self.log(f'V={self.grafo.total_vertices}  E={self.grafo.total_arestas}', 'info')
        except Exception as e:
            self.log(f'Erro: {e}', 'err')

    def vertice_mais_proximo(self, sx, sy, max_px=14):
        if self.grafo is None:
            return -1
        wx, wy = self.cam.tela_para_mundo(sx, sy)
        melhor, melhor_d2 = -1, float('inf')
        for v in self.grafo.vertices:
            if v is None:
                continue
            d2 = (v.x - wx) ** 2 + (v.y - wy) ** 2
            if d2 < melhor_d2:
                melhor_d2 = d2
                melhor = v.id
        if melhor >= 0:
            sx2, sy2 = self.cam.mundo_para_tela(self.grafo.vertices[melhor].x, self.grafo.vertices[melhor].y)
            if math.hypot(sx - sx2, sy - sy2) <= max_px:
                return melhor
        return -1

    def _distancia_ponto_segmento(self, px, py, ax, ay, bx, by):
        abx = bx - ax
        aby = by - ay
        apx = px - ax
        apy = py - ay
        ab2 = abx * abx + aby * aby
        if ab2 == 0:
            return math.hypot(apx, apy)
        t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
        cx = ax + t * abx
        cy = ay + t * aby
        return math.hypot(px - cx, py - cy)

    def aresta_mais_proxima(self, sx, sy, max_px=8):
        if self.grafo is None:
            return None

        wx, wy = self.cam.tela_para_mundo(sx, sy)
        melhor = None
        melhor_d = float('inf')

        for idx, (u, v, directed) in enumerate(self.grafo.arestas_raw):
            vu = self.grafo.vertices[u]
            vv = self.grafo.vertices[v]
            if vu is None or vv is None:
                continue
            d = self._distancia_ponto_segmento(wx, wy, vu.x, vu.y, vv.x, vv.y)
            if d < melhor_d:
                melhor_d = d
                melhor = (idx, u, v, directed)

        if melhor is None:
            return None

        _, u, v, directed = melhor
        p1 = self.cam.mundo_para_tela(self.grafo.vertices[u].x, self.grafo.vertices[u].y)
        p2 = self.cam.mundo_para_tela(self.grafo.vertices[v].x, self.grafo.vertices[v].y)
        if self._distancia_ponto_segmento(sx, sy, p1[0], p1[1], p2[0], p2[1]) <= max_px:
            return melhor
        return None

    def desenhar_grafo(self, surf):
        if self.grafo is None:
            return

        # Area do grafo (usada apenas para dimensões). Ao desenhar, não
        # filtramos vértices por colisão com a área para garantir que IDs e
        # pesos apareçam consistentemente durante pan/zoom.
        area = self.area_grafo()
        cam = self.cam
        caminho_set_pares = set()
        for i in range(len(self.caminho) - 1):
            a, b = self.caminho[i], self.caminho[i + 1]
            caminho_set_pares.add((min(a, b), max(a, b)))

        for (u, v, directed) in self.grafo.arestas_raw:
            vu = self.grafo.vertices[u]
            vv = self.grafo.vertices[v]
            if vu is None or vv is None:
                continue
            p1 = cam.mundo_para_tela(vu.x, vu.y)
            p2 = cam.mundo_para_tela(vv.x, vv.y)

            par = (min(u, v), max(u, v))
            no_caminho = par in caminho_set_pares

            if no_caminho:
                cor = COR_CAMINHO_A
                larg = max(2, int(self.esp_aresta * 3))
            elif directed:
                cor = COR_ARESTA_DIR
                larg = max(1, int(self.esp_aresta))
            else:
                cor = COR_ARESTA
                larg = max(1, int(self.esp_aresta))

            pygame.draw.line(surf, cor, p1, p2, larg)

            if directed and cam.escala > 0.3:
                mx = (p1[0] + p2[0]) // 2
                my = (p1[1] + p2[1]) // 2
                ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
                sz = 5
                ponta = [
                    (mx, my),
                    (int(mx - sz * math.cos(ang - 0.4)), int(my - sz * math.sin(ang - 0.4))),
                    (int(mx - sz * math.cos(ang + 0.4)), int(my - sz * math.sin(ang + 0.4))),
                ]
                pygame.draw.polygon(surf, cor, ponta)

            if self.mostrar_pesos:
                # Mostrar pesos independente do zoom quando a opção estiver ativa.
                try:
                    d = math.hypot(vu.x - vv.x, vu.y - vv.y)
                    txt = self.fonte_sm.render(f'{d:.0f}', True, COR_TEXTO_DIM)
                    surf.blit(txt, ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2))
                except Exception:
                    pass

        for v in self.grafo.vertices:
            if v is None:
                continue
            sx, sy = cam.mundo_para_tela(v.x, v.y)

            r = max(1, int(self.tam_vertice))

            if v.id == self.origem:
                cor = COR_ORIGEM
                r = max(5, r * 2)
            elif v.id == self.destino:
                cor = COR_DESTINO
                r = max(5, r * 2)
            elif v.id in self.caminho_set:
                cor = COR_CAMINHO_V
                r = max(3, int(r * 1.5))
            else:
                cor = COR_VERTICE

            if r < 1:
                continue
            pygame.draw.circle(surf, cor, (sx, sy), r)

            if self.mostrar_ids:
                # Mostrar IDs independente do zoom quando a opção estiver ativa.
                try:
                    desloc = max(4, r) + 2
                    txt = self.fonte_sm.render(str(v.id), True, COR_TEXTO_INFO)
                    surf.blit(txt, (sx + desloc, sy - 5))
                except Exception:
                    pass

        for vid, label, cor in [(self.origem, 'O', COR_ORIGEM), (self.destino, 'D', COR_DESTINO)]:
            if vid < 0:
                continue
            v = self.grafo.vertices[vid]
            if v is None:
                continue
            sx, sy = cam.mundo_para_tela(v.x, v.y)
            r = max(8, int(self.tam_vertice * 3))
            pygame.draw.circle(surf, cor, (sx, sy), r, 2)
            txt = self.fonte_lg.render(label, True, cor)
            surf.blit(txt, (sx - txt.get_width() // 2, sy - txt.get_height() // 2))

    def desenhar_sidebar(self, surf):
        W, H = self.screen.get_size()
        pygame.draw.rect(surf, COR_SIDEBAR, (0, 0, SIDEBAR_W, H))
        pygame.draw.line(surf, COR_BORDA, (SIDEBAR_W, 0), (SIDEBAR_W, H), 1)

        # Cabeçalho maior para título e descrições
        pygame.draw.rect(surf, COR_PAINEL, (0, 0, SIDEBAR_W, 72))
        t = self.fonte_xl.render('NavGrafo UFG', True, COR_TEXTO_INFO)
        surf.blit(t, (8, 8))
        sub = self.fonte_sm.render('AED2 2026-1 | Dijkstra', True, COR_TEXTO_DIM)
        surf.blit(sub, (8, 40))

        for b in self.botoes.values():
            b.desenhar(surf, self.fonte_sm)

        y = self._y_stats
        pygame.draw.line(surf, COR_BORDA, (8, y - 4), (SIDEBAR_W - 8, y - 4), 1)

        def stat(label, valor, cor=COR_TEXTO_INFO):
            nonlocal y
            l = self.fonte_log.render(label, True, COR_TEXTO_DIM)
            v = self.fonte_log.render(str(valor), True, cor)
            surf.blit(l, (8, y))
            surf.blit(v, (SIDEBAR_W - v.get_width() - 8, y))
            y += self.fonte_log.get_linesize() + 2

        stat('Vértices:', self.grafo.total_vertices if self.grafo else 0)
        stat('Arestas:', self.grafo.total_arestas if self.grafo else 0)
        stat('Origem:', self.origem if self.origem >= 0 else '—')
        stat('Destino:', self.destino if self.destino >= 0 else '—')
        stat('Distância:', f'{self.caminho_dist:.1f} u.' if self.caminho else '—', COR_TEXTO_OK if self.caminho else COR_TEXTO_DIM)
        stat('Nós explorados:', self.nos_explorados if self.caminho else '—')
        stat('Nós no caminho:', len(self.caminho) if self.caminho else '—')
        stat('Tempo (ms):', f'{self.tempo_ms:.1f}' if self.caminho else '—')

        y = self._y_log
        if y < H:
            pygame.draw.line(surf, COR_BORDA, (8, y - 4), (SIDEBAR_W - 8, y - 4), 1)
            line_h = self.fonte_log.get_linesize() + 2
            linhas_vis = max(1, (H - y) // line_h)
            for msg, cor in self.log_msgs[-linhas_vis:]:
                txt = self.fonte_log.render(f'> {msg}', True, cor)
                surf.blit(txt, (8, y))
                y += line_h

    def desenhar_statusbar(self, surf):
        W, H = self.screen.get_size()
        pygame.draw.rect(surf, COR_PAINEL, (0, H - 22, W, 22))
        pygame.draw.line(surf, COR_BORDA, (0, H - 22), (W, H - 22), 1)
        zoom_pct = int(self.cam.escala * 100)
        modo_txt = self.modo.replace('_', ' ').upper()
        s = f'MODO: {modo_txt}   |   Zoom: {zoom_pct}%   |   V:{self.grafo.total_vertices if self.grafo else 0}  E:{self.grafo.total_arestas if self.grafo else 0}'
        if self.arq_carregado:
            s += f'   |   {self.arq_carregado}'
        txt = self.fonte_sm.render(s, True, COR_TEXTO_DIM)
        surf.blit(txt, (SIDEBAR_W + 8, H - 17))

    def desenhar(self):
        W, H = self.screen.get_size()
        self.screen.fill(COR_FUNDO)
        area = self.area_grafo()

        grafo_surf = pygame.Surface((area.width, area.height))
        grafo_surf.fill(COR_FUNDO)
        cam_backup_x = self.cam.x
        self.cam.x -= SIDEBAR_W
        self.desenhar_grafo(grafo_surf)
        self.cam.x = cam_backup_x
        self.ultimo_grafo_surf = grafo_surf.copy()
        self.screen.blit(grafo_surf, (SIDEBAR_W, 0))

        self.desenhar_sidebar(self.screen)
        self.desenhar_statusbar(self.screen)
        pygame.display.flip()

    def handle_click(self, sx, sy, botao_mouse):
        for nome, btn in self.botoes.items():
            if btn.clicado((sx, sy)):
                self.handle_botao(nome)
                return

        if sx <= SIDEBAR_W or self.modo == 'pan' or self.grafo is None:
            return

        vid = self.vertice_mais_proximo(sx, sy)

        if self.modo == 'origem':
            if vid >= 0:
                self.origem = vid
                self.log(f'Origem: {vid}', 'ok')
            else:
                self.log('Clique mais perto de um vértice', 'warn')

        elif self.modo == 'destino':
            if vid >= 0:
                self.destino = vid
                self.log(f'Destino: {vid}', 'ok')
            else:
                self.log('Clique mais perto de um vértice', 'warn')

        elif self.modo == 'add_vertice':
            wx, wy = self.cam.tela_para_mundo(sx, sy)
            nid = self.grafo.adicionar_vertice(wx, wy)
            self.log(f'Vértice {nid} adicionado', 'ok')

        elif self.modo in ('add_aresta', 'add_aresta_dir'):
            if vid >= 0:
                if self.add_aresta_primeiro < 0:
                    self.add_aresta_primeiro = vid
                    self.log(f'1º vértice: {vid} — clique no 2º', 'info')
                else:
                    u = self.add_aresta_primeiro
                    directed = self.modo == 'add_aresta_dir'
                    d = self.grafo.adicionar_aresta(u, vid, directed)
                    tipo = 'mão única' if directed else 'mão dupla'
                    self.log(f'Aresta {u}→{vid} ({tipo}, d={d:.1f})', 'ok')
                    self.add_aresta_primeiro = -1

        elif self.modo == 'deletar':
            if vid >= 0:
                self.grafo.remover_vertice(vid)
                if self.origem == vid:
                    self.origem = -1
                if self.destino == vid:
                    self.destino = -1
                self.caminho = []
                self.caminho_set = set()
                self.log(f'Vértice {vid} removido', 'warn')
            else:
                self.log('Nenhum vértice próximo', 'warn')

        elif self.modo == 'deletar_aresta':
            alvo = self.aresta_mais_proxima(sx, sy)
            if alvo is None:
                self.log('Nenhuma aresta próxima', 'warn')
                return

            _, u, v, directed = alvo
            if self.grafo.remover_aresta(u, v, directed):
                self.caminho = []
                self.caminho_set = set()
                tipo = 'dirigida' if directed else 'não-dirigida'
                self.log(f'Aresta {u}↔{v} removida ({tipo})', 'warn')
            else:
                self.log('Falha ao remover aresta', 'err')

    def handle_botao(self, nome):
        mapa_modos = {
            'modo_orig': 'origem',
            'modo_dest': 'destino',
            'modo_addv': 'add_vertice',
            'modo_adde': 'add_aresta',
            'modo_addd': 'add_aresta_dir',
            'modo_del': 'deletar',
            'modo_dela': 'deletar_aresta',
            'modo_pan': 'pan',
        }
        if nome in mapa_modos:
            self.set_modo(mapa_modos[nome])
        elif nome == 'ler_poly':
            self.pedir_arquivo()
        elif nome == 'dijkstra':
            self.executar_dijkstra()
        elif nome == 'limpar':
            self.limpar_selecao()
        elif nome == 'fit':
            if self.grafo is not None:
                area = self.area_grafo()
                self.cam.fit(self.grafo.vertices, area.width, area.height)
                self.cam.x += SIDEBAR_W
        elif nome == 'tog_ids':
            self.mostrar_ids = not self.mostrar_ids
            self.log(f'IDs: {"ON" if self.mostrar_ids else "off"}', 'info')
            self._layout_botoes()
        elif nome == 'tog_pesos':
            self.mostrar_pesos = not self.mostrar_pesos
            self.log(f'Pesos: {"ON" if self.mostrar_pesos else "off"}', 'info')
            self._layout_botoes()
        elif nome == 'copiar':
            self.copiar_imagem()
        elif nome == 'sair':
            pygame.quit()
            sys.exit()

    def pedir_arquivo(self):
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            caminho = filedialog.askopenfilename(
                title='Selecione um mapa',
                filetypes=[
                    ('Mapas suportados', '*.poly *.txt *.csv *.tsv *.dat *.osm *.xml *.xlml'),
                    ('Poly files', '*.poly'),
                    ('Text files', '*.txt *.csv *.tsv *.dat'),
                    ('OSM/XML files', '*.osm *.xml *.xlml'),
                    ('All', '*.*'),
                ],
            )
            root.destroy()
            if caminho:
                self.carregar_arquivo(caminho)
        except ImportError:
            poly_files = [f for f in os.listdir('.') if f.endswith('.poly')]
            if poly_files:
                self.carregar_arquivo(poly_files[0])
                self.log('Dica: coloque o .poly na mesma pasta', 'info')
            else:
                self.log('Coloque o .poly na mesma pasta e tente novamente', 'warn')
                self.log('Ou use: python main.py arquivo.poly', 'info')

    def executar_dijkstra(self):
        if self.grafo is None:
            self.log('Carregue um grafo primeiro', 'err')
            return
        if self.origem < 0 or self.destino < 0:
            self.log('Defina Origem e Destino primeiro', 'err')
            return
        if self.origem == self.destino:
            self.log('Origem = Destino', 'warn')
            return
        if self.grafo.total_vertices == 0:
            self.log('Carregue um grafo primeiro', 'err')
            return

        self.log(f'Dijkstra: {self.origem} → {self.destino}...', 'info')
        cam, dist_total, explorados, tempo = dijkstra(self.grafo, self.origem, self.destino)

        self.caminho = cam
        self.caminho_set = set(cam)
        self.caminho_dist = dist_total
        self.nos_explorados = explorados
        self.tempo_ms = tempo

        if not cam:
            self.log('Sem caminho!', 'err')
        else:
            self.log(f'Rota: {len(cam)} vértices, dist={dist_total:.1f}', 'ok')
            self.log(f'Explorados: {explorados} | Tempo: {tempo:.1f}ms', 'info')
            preview = '→'.join(str(x) for x in cam[:6])
            if len(cam) > 6:
                preview += '→...'
            self.log(preview, 'ok')

    def limpar_selecao(self):
        self.origem = self.destino = -1
        self.caminho = []
        self.caminho_set = set()
        self.caminho_dist = 0.0
        self.nos_explorados = 0
        self.tempo_ms = 0.0
        self.log('Seleção limpa', 'warn')

    def copiar_imagem(self):
        try:
            surf = self.ultimo_grafo_surf
            if surf is None:
                self.log('Nenhuma imagem disponível para copiar', 'warn')
                return

            largura, altura = surf.get_size()
            # Garantir formato 32-bit com alpha para tobytes ser consistente
            try:
                surf32 = surf.convert_alpha()
            except Exception:
                surf32 = surf.copy()
            rgba = pygame.image.tobytes(surf32, 'RGBA')
            # Converte RGBA->BGRA
            bgra = bytearray(len(rgba))
            bgra[0::4] = rgba[2::4]
            bgra[1::4] = rgba[1::4]
            bgra[2::4] = rgba[0::4]
            bgra[3::4] = rgba[3::4]

            # Tentar criar um HBITMAP via CreateDIBSection (melhor compatibilidade)
            try:
                gdi32 = ctypes.windll.gdi32
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32

                class BITMAPINFOHEADER(ctypes.Structure):
                    _fields_ = [
                        ('biSize', ctypes.c_uint32),
                        ('biWidth', ctypes.c_int32),
                        ('biHeight', ctypes.c_int32),
                        ('biPlanes', ctypes.c_uint16),
                        ('biBitCount', ctypes.c_uint16),
                        ('biCompression', ctypes.c_uint32),
                        ('biSizeImage', ctypes.c_uint32),
                        ('biXPelsPerMeter', ctypes.c_int32),
                        ('biYPelsPerMeter', ctypes.c_int32),
                        ('biClrUsed', ctypes.c_uint32),
                        ('biClrImportant', ctypes.c_uint32),
                    ]

                header = BITMAPINFOHEADER()
                header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
                header.biWidth = largura
                # Use altura positiva e copie linhas invertidas (bottom-up) para DIB
                header.biHeight = altura
                header.biPlanes = 1
                header.biBitCount = 32
                header.biCompression = 0  # BI_RGB
                header.biSizeImage = len(bgra)
                header.biXPelsPerMeter = 0
                header.biYPelsPerMeter = 0
                header.biClrUsed = 0
                header.biClrImportant = 0

                ppvBits = ctypes.c_void_p()
                # CreateDIBSection(hdc=NULL, pbmi=&header, usage=0, ppvBits, NULL, 0)
                hbm = gdi32.CreateDIBSection(0, ctypes.byref(header), 0, ctypes.byref(ppvBits), None, 0)
                if hbm:
                    # Copiar dados de pixels: DIB bottom-up (linha 0 = última linha)
                    row_bytes = largura * 4
                    for y in range(altura):
                        src_off = (altura - 1 - y) * row_bytes
                        dest_off = y * row_bytes
                        dest_ptr = ppvBits.value + dest_off
                        src_slice = (ctypes.c_ubyte * row_bytes).from_buffer(bgra, src_off)
                        ctypes.memmove(dest_ptr, src_slice, row_bytes)

                    # Colocar HBITMAP no clipboard como CF_BITMAP (2)
                    CF_BITMAP = 2
                    # Abrir clipboard com retries (pode estar ocupado)
                    opened = False
                    for _ in range(6):
                        if user32.OpenClipboard(None):
                            opened = True
                            break
                        time.sleep(0.05)
                    if not opened:
                        # Cleanup HBITMAP if we can't open clipboard
                        gdi32.DeleteObject(hbm)
                        raise RuntimeError('Falha ao abrir clipboard (CreateDIBSection path)')
                    try:
                        user32.EmptyClipboard()
                        if not user32.SetClipboardData(CF_BITMAP, hbm):
                            # Se SetClipboardData falhar, liberar HBITMAP
                            gdi32.DeleteObject(hbm)
                            raise RuntimeError('Falha ao SetClipboardData(CF_BITMAP)')
                        # Sucesso: o sistema Windows assume ownership do HBITMAP
                        hbm = None
                    finally:
                        user32.CloseClipboard()

                    self.log('Imagem do grafo copiada para a área de transferência (HBITMAP)', 'ok')
                    return
            except Exception:
                # Se algo falhar no caminho HBITMAP, tentamos DIB diretamente
                pass

            # Fallback: usar CF_DIB (BITMAPINFOHEADER + pixels em global memory)
            class BITMAPINFOHEADER2(ctypes.Structure):
                _fields_ = [
                    ('biSize', ctypes.c_uint32),
                    ('biWidth', ctypes.c_int32),
                    ('biHeight', ctypes.c_int32),
                    ('biPlanes', ctypes.c_uint16),
                    ('biBitCount', ctypes.c_uint16),
                    ('biCompression', ctypes.c_uint32),
                    ('biSizeImage', ctypes.c_uint32),
                    ('biXPelsPerMeter', ctypes.c_int32),
                    ('biYPelsPerMeter', ctypes.c_int32),
                    ('biClrUsed', ctypes.c_uint32),
                    ('biClrImportant', ctypes.c_uint32),
                ]

            header2 = BITMAPINFOHEADER2()
            header2.biSize = ctypes.sizeof(BITMAPINFOHEADER2)
            header2.biWidth = largura
            # altura negativa para indicar top-down (ordem do Pygame)
            header2.biHeight = -altura
            header2.biPlanes = 1
            header2.biBitCount = 32
            header2.biCompression = 0
            header2.biSizeImage = len(bgra)

            header_size = ctypes.sizeof(header2)
            total_size = header_size + len(bgra)

            GMEM_MOVEABLE = 0x0002
            mem = ctypes.windll.kernel32.GlobalAlloc(GMEM_MOVEABLE, total_size)
            if not mem:
                raise RuntimeError('Falha ao alocar memória para clipboard (DIB fallback)')

            ptr = ctypes.windll.kernel32.GlobalLock(mem)
            if not ptr:
                ctypes.windll.kernel32.GlobalFree(mem)
                raise RuntimeError('Falha ao travar memória para clipboard (DIB fallback)')

            try:
                ctypes.memmove(ptr, ctypes.byref(header2), header_size)
                dest = ptr + header_size
                ctypes.memmove(dest, (ctypes.c_ubyte * len(bgra)).from_buffer(bgra), len(bgra))
            finally:
                ctypes.windll.kernel32.GlobalUnlock(mem)

            CF_DIB = 8
            # Abrir clipboard com retries
            opened = False
            for _ in range(6):
                if ctypes.windll.user32.OpenClipboard(None):
                    opened = True
                    break
                time.sleep(0.05)
            if not opened:
                ctypes.windll.kernel32.GlobalFree(mem)
                raise RuntimeError('Falha ao abrir a área de transferência (DIB fallback)')

            try:
                ctypes.windll.user32.EmptyClipboard()
                if not ctypes.windll.user32.SetClipboardData(CF_DIB, mem):
                    raise RuntimeError('Falha ao copiar para a área de transferência (DIB fallback)')
                mem = None
            finally:
                ctypes.windll.user32.CloseClipboard()

            self.log('Imagem do grafo copiada para a área de transferência (DIB fallback)', 'ok')
        except Exception as e:
            try:
                nome = f'grafo_{int(time.time())}.png'
                pygame.image.save(self.screen, nome)
                self.log(f'Clipboard indisponível; salvo em arquivo: {nome}', 'warn')
            except Exception as fallback_error:
                self.log(f'Erro ao copiar/salvar: {e} | fallback: {fallback_error}', 'err')

    def run(self):
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            self.carregar_arquivo(sys.argv[1])
        else:
            mapas = [f for f in os.listdir('.') if f.lower().endswith(('.poly', '.txt', '.csv', '.tsv', '.dat', '.osm', '.xml', '.xlml'))]
            if mapas:
                self.carregar_arquivo(mapas[0])
            else:
                self.log('Nenhum mapa suportado encontrado.', 'warn')
                self.log('Use: python main.py arquivo.poly|txt|osm|xml', 'info')

        running = True
        while running:
            W, H = self.screen.get_size()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._layout_botoes()
                elif event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    for b in self.botoes.values():
                        b.checar_hover(pos)
                    if self.pan_ativo:
                        dx = pos[0] - self.pan_start[0]
                        dy = pos[1] - self.pan_start[1]
                        self.cam.x = self.cam_start[0] + dx
                        self.cam.y = self.cam_start[1] + dy
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.modo == 'pan':
                            self.pan_ativo = True
                            self.pan_start = event.pos
                            self.cam_start = (self.cam.x, self.cam.y)
                        else:
                            self.handle_click(*event.pos, 1)
                    elif event.button == 2:
                        self.pan_ativo = True
                        self.pan_start = event.pos
                        self.cam_start = (self.cam.x, self.cam.y)
                    elif event.button == 4:
                        self.cam.zoom(1.15, *event.pos)
                    elif event.button == 5:
                        self.cam.zoom(1 / 1.15, *event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button in (1, 2):
                        self.pan_ativo = False
                elif event.type == pygame.KEYDOWN:
                    k = event.key
                    if k == pygame.K_q:
                        running = False
                    elif k == pygame.K_o:
                        self.set_modo('origem')
                    elif k == pygame.K_d:
                        self.set_modo('destino')
                    elif k == pygame.K_c:
                        self.executar_dijkstra()
                    elif k == pygame.K_p:
                        self.set_modo('pan')
                    elif k == pygame.K_f:
                        if self.grafo is not None:
                            area = self.area_grafo()
                            self.cam.fit(self.grafo.vertices, area.width, area.height)
                            self.cam.x += SIDEBAR_W
                    elif k == pygame.K_r:
                        self.limpar_selecao()
                    elif k == pygame.K_v:
                        self.set_modo('add_vertice')
                    elif k == pygame.K_a:
                        self.set_modo('add_aresta')
                    elif k == pygame.K_u:
                        self.set_modo('add_aresta_dir')
                    elif k == pygame.K_x:
                        self.set_modo('deletar')
                    elif k == pygame.K_z:
                        self.set_modo('deletar_aresta')
                    elif k == pygame.K_l:
                        self.pedir_arquivo()
                    elif k == pygame.K_n:
                        self.handle_botao('tog_ids')
                    elif k == pygame.K_w:
                        self.handle_botao('tog_pesos')
                    elif k == pygame.K_i:
                        self.copiar_imagem()
                    elif k == pygame.K_PLUS or k == pygame.K_EQUALS:
                        cx, cy = W // 2, H // 2
                        self.cam.zoom(1.2, cx, cy)
                    elif k == pygame.K_MINUS:
                        cx, cy = W // 2, H // 2
                        self.cam.zoom(1 / 1.2, cx, cy)

            self.desenhar()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == '__main__':
    App().run()