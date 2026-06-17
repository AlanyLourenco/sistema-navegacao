"""
Componentes de interface e constantes visuais do sistema.

1. Para que serve o arquivo:
     - Centraliza as constantes visuais (cores, tamanhos) e componentes UI leves
         usados pela aplicação: `Camera` e `Botao`.

2. Como funciona (resumo):
     - `Camera` converte coordenadas mundo↔tela, controla zoom e faz o `fit`
         automático do mapa no espaço disponível.
     - `Botao` encapsula retângulo, estado de hover/ativo e desenho simples.

3. Quais requisitos atende:
     - RNF06: Interface intuitiva — componentes reutilizáveis e constantes bem
         definidas facilitam manutenção do visual.
     - RNF05: Otimizações visuais simples (evitar desenho desnecessário no `fit`).

Notas de manutenção:
     - Ajuste de `SIDEBAR_W`, `FPS` e cores afeta toda a aplicação; manter
         consistência ao alterar.
"""

import pygame


LARGURA, ALTURA = 1280, 780
FPS = 60
SIDEBAR_W = 260

COR_FUNDO = (10, 15, 26)
COR_ARESTA = (26, 46, 74)
COR_ARESTA_DIR = (60, 90, 40)
COR_VERTICE = (26, 58, 90)
COR_ORIGEM = (74, 212, 138)
COR_DESTINO = (212, 90, 74)
COR_CAMINHO_A = (0, 212, 255)
COR_CAMINHO_V = (0, 180, 220)
COR_SIDEBAR = (8, 13, 24)
COR_PAINEL = (13, 20, 36)
COR_TEXTO = (200, 216, 232)
COR_TEXTO_DIM = (64, 80, 96)
COR_TEXTO_INFO = (74, 159, 212)
COR_TEXTO_OK = (74, 212, 138)
COR_TEXTO_WARN = (212, 168, 74)
COR_TEXTO_ERR = (212, 90, 74)
COR_BORDA = (30, 48, 80)
COR_BTN = (13, 26, 46)
COR_BTN_HOVER = (26, 42, 68)
COR_BTN_ATIVO = (20, 60, 100)


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.escala = 1.0

    def mundo_para_tela(self, wx, wy):
        sx = wx * self.escala + self.x
        sy = wy * self.escala + self.y
        return int(sx), int(sy)

    def tela_para_mundo(self, sx, sy):
        wx = (sx - self.x) / self.escala
        wy = (sy - self.y) / self.escala
        return wx, wy

    def zoom(self, fator, pivot_sx, pivot_sy):
        nova = max(0.01, min(200.0, self.escala * fator))
        self.x = pivot_sx - (pivot_sx - self.x) * nova / self.escala
        self.y = pivot_sy - (pivot_sy - self.y) * nova / self.escala
        self.escala = nova

    def fit(self, vertices, area_w, area_h):
        vivos = [v for v in vertices if v is not None]
        if not vivos:
            return
        minx = min(v.x for v in vivos)
        maxx = max(v.x for v in vivos)
        miny = min(v.y for v in vivos)
        maxy = max(v.y for v in vivos)
        gw = maxx - minx or 1
        gh = maxy - miny or 1
        self.escala = min(area_w / gw, area_h / gh) * 0.9
        self.x = (area_w - gw * self.escala) / 2 - minx * self.escala
        self.y = (area_h - gh * self.escala) / 2 - miny * self.escala


class Botao:
    def __init__(self, x, y, w, h, texto, cor_texto=None, ativo=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.cor_texto = cor_texto or COR_TEXTO_INFO
        self.ativo = ativo
        self.hover = False

    def desenhar(self, surf, fonte):
        cor_bg = COR_BTN_ATIVO if self.ativo else (COR_BTN_HOVER if self.hover else COR_BTN)
        pygame.draw.rect(surf, cor_bg, self.rect, border_radius=4)
        pygame.draw.rect(surf, COR_BORDA, self.rect, 1, border_radius=4)
        txt = fonte.render(self.texto, True, self.cor_texto if self.ativo or self.hover else COR_TEXTO_DIM)
        r = txt.get_rect(center=self.rect.center)
        surf.blit(txt, r)

    def checar_hover(self, pos, scroll=0):
        # `scroll` é o offset vertical atual da sidebar; ao desenhar, os botões
        # são deslocados em y por `-scroll`. Aqui usamos uma cópia deslocada
        # para verificar hover sem alterar a posição real do botão.
        rect = self.rect.move(0, -scroll)
        self.hover = rect.collidepoint(pos)

    def clicado(self, pos, scroll=0):
        rect = self.rect.move(0, -scroll)
        return rect.collidepoint(pos)

    def desenhar(self, surf, fonte, scroll=0):
        # Desenha o botão deslocado verticalmente de acordo com `scroll`.
        rect = self.rect.move(0, -scroll)
        cor_bg = COR_BTN_ATIVO if self.ativo else (COR_BTN_HOVER if self.hover else COR_BTN)
        pygame.draw.rect(surf, cor_bg, rect, border_radius=4)
        pygame.draw.rect(surf, COR_BORDA, rect, 1, border_radius=4)
        txt = fonte.render(self.texto, True, self.cor_texto if self.ativo or self.hover else COR_TEXTO_DIM)
        r = txt.get_rect(center=rect.center)
        surf.blit(txt, r)