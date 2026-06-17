# NavGrafo UFG — Sistema de Navegação em Grafos
**AED2 2026-1 — Prof. André L. Moura**

## Requisitos
- Python 3.8+
- Pygame: `pip install pygame`

## Como executar

```bash
# Passando um arquivo suportado direto:
python main.py Campus2UFG_Regiao.poly
python main.py mapa.osm
python main.py mapa.xml
python main.py mapa.txt

# Ou sem argumento (busca um mapa suportado na pasta atual):
python main.py
```

> O arquivo `nav_grafo_ufg.py` foi mantido apenas como launcher de compatibilidade.

## Controles

| Tecla / Ação | Função |
|---|---|
| `O` | Modo: selecionar Origem (clique no vértice) |
| `D` | Modo: selecionar Destino (clique no vértice) |
| `C` | Calcular menor caminho (Dijkstra) |
| `P` | Modo Pan (mover o mapa) |
| `F` | Ajustar mapa à tela (fit) |
| `R` | Limpar seleção |
| `V` | Adicionar vértice (clique no mapa) |
| `A` | Adicionar aresta não-dirigida (clique em 2 vértices) |
| `U` | Adicionar aresta dirigida/mão única |
| `X` | Deletar vértice (clique nele) |
| `Z` | Deletar aresta (clique na aresta) |
| `N` | Mostrar/ocultar IDs dos vértices |
| `W` | Mostrar/ocultar pesos das arestas |
| `L` | Importar mapa (.poly, .txt, .osm, .xml) |
| `I` | Copiar imagem do mapa para o clipboard (Windows: PowerShell; Linux: xclip; macOS: osascript) — fallback salva PNG |
| `Q` | Sair |
| Scroll do mouse | Zoom in/out |
| Botão do meio | Pan temporário |
| `+` / `-` | Zoom in/out pelo teclado |

## Arquivos de entrada suportados
- `.poly` — formato gerado pelo `LeArqOSM_e_GeraArqPoly.c`
- `.osm` / `.xml` / `.xlml` — leitura direta de OSM/XML com nós e vias `highway`
- `.txt` / `.csv` / `.tsv` / `.dat` — formato estruturado com seções `VERTICES` e `ARESTAS`

Exemplo de TXT estruturado:

```txt
VERTICES
0 100.0 120.0 Rua_A
1 180.0 130.0 Rua_B
2 220.0 160.0 Av_C

ARESTAS
0 1 0
1 2 1
```

Observação: em TXT, o terceiro campo da aresta é opcional e indica direção quando vale `1`, `d`, `dir`, `directed`, `oneway` ou `->`.

## Algoritmo
Dijkstra com **Min-Heap** (módulo `heapq` do Python) — complexidade O((V+E) lg V).
Suporta grafos com milhares de vértices (Campus UFG: 10.000 V, 11.526 E).

## Requisitos satisfeitos
- RF01: Importa .poly com coordenadas reais
- RF02: Enumera os vértices e exibe os pesos das arestas (teclas N e W)
- RF03: Seleção de origem (verde) e destino (vermelho), com desfazer via R
- RF04: Caminho mínimo destacado em ciano
- RF05: Adição/remoção de vértices e arestas por clique
- RF06: Arestas dirigidas (mão única) e não-dirigidas (mão dupla)
- RF07: Tempo, nós explorados, distância total exibidos no painel
- RF08: Tecla `I` copia imagem para clipboard (ou salva PNG como fallback)
- RNF01-08: Cores distintas, interface intuitiva, código modular
