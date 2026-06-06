# NavGrafo UFG — Sistema de Navegação em Grafos
**AED2 2026-1 — Prof. André L. Moura**

## Requisitos
- Python 3.8+
- Pygame: `pip install pygame`

## Como executar

```bash
# Passando o arquivo .poly direto:
python main.py Campus2UFG_Regiao.poly

# Ou sem argumento (busca .poly na pasta atual):
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
| `N` | Mostrar/ocultar IDs dos vértices |
| `W` | Mostrar/ocultar pesos das arestas |
| `L` | Carregar arquivo .poly |
| `I` | Salvar imagem do mapa (screenshot) |
| `Q` | Sair |
| Scroll do mouse | Zoom in/out |
| Botão do meio | Pan temporário |
| `+` / `-` | Zoom in/out pelo teclado |

## Arquivos de entrada suportados
- `.poly` — formato gerado pelo `LeArqOSM_e_GeraArqPoly.c`
- Estrutura: `num_vertices dim 0 1` → linhas `id x y` → `num_arestas 1` → linhas `id src dst dirigida`

## Algoritmo
Dijkstra com **Min-Heap** (módulo `heapq` do Python) — complexidade O((V+E) lg V).
Suporta grafos com milhares de vértices (Campus UFG: 10.000 V, 11.526 E).

## Requisitos satisfeitos
- RF01: Importa .poly com coordenadas reais
- RF02: Exibe IDs e pesos (teclas N e W)
- RF03: Seleção de origem (verde) e destino (vermelho), com desfazer via R
- RF04: Caminho mínimo destacado em ciano
- RF05: Adição/remoção de vértices e arestas por clique
- RF06: Arestas dirigidas (mão única) e não-dirigidas (mão dupla)
- RF07: Tempo, nós explorados, distância total exibidos no painel
- RF08: Tecla I salva screenshot
- RNF01-08: Cores distintas, interface intuitiva, código modular
