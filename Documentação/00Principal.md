# NavGrafo UFG — Sistema de Navegação Primitivo em Grafos

> **Disciplina:** Algoritmos e Estruturas de Dados 2 (AED2) — 2026/1  
> **Professor:** André L. Moura  
> **Curso:** Ciência da Computação — Universidade Federal de Goiás (UFG)  
> **Linguagem:** Python 3.11 · Interface: Pygame · Algoritmo central: Dijkstra + Min-Heap

---

## O que é este projeto?

O **NavGrafo UFG** é um sistema de navegação interativa em grafos construído como projeto prático de AED2. A aplicação permite importar mapas reais (OpenStreetMap, `.poly`, `.txt`), visualizá-los como grafos ponderados e calcular o **caminho mínimo** entre dois pontos usando o **Algoritmo de Dijkstra com Min-Heap**.

O Campus 2 da UFG possui aproximadamente **10.000 vértices** e **11.526 arestas** no arquivo de mapa padrão — escala real que exige implementações eficientes, não apenas funcionais.

---

## Instalação e execução rápida

**Pré-requisito:** Python 3.8+ e Pygame.

```bash
pip install pygame

# Com mapa explícito (recomendado):
python main.py Campus2UFG_Regiao.poly
python main.py mapa.osm
python main.py mapa.txt

# Sem argumento — detecta mapa automaticamente na pasta:
python main.py

# Launcher de compatibilidade:
python nav_grafo_ufg.py Campus2UFG_Regiao.poly
```

**Estrutura de arquivos esperada:**

```
projeto/
├── main.py
├── core.py
├── algorithms.py
├── gui.py
├── nav_grafo_ufg.py
├── README.md
└── Campus2UFG_Regiao.poly
```

---

## Controles da interface

| Tecla / Ação | Função |
|---|---|
| `O` | Modo: selecionar **Origem** (verde) |
| `D` | Modo: selecionar **Destino** (vermelho) |
| `C` | **Calcular** caminho mínimo (Dijkstra) |
| `R` | Limpar seleção |
| `P` | Modo Pan — arrastar o mapa |
| `F` | Ajustar mapa à tela (fit automático) |
| `V` | Adicionar **vértice** |
| `A` | Adicionar **aresta não-dirigida** |
| `U` | Adicionar **aresta dirigida** (mão única) |
| `X` | Deletar **vértice** |
| `Z` | Deletar **aresta** |
| `N` | Mostrar/ocultar IDs dos vértices |
| `W` | Mostrar/ocultar pesos das arestas |
| `L` | **Importar** mapa |
| `I` | **Copiar imagem** para área de transferência |
| `Q` | Sair |
| Scroll do mouse | Zoom in/out |
| Botão do meio (drag) | Pan temporário |
| `+` / `-` | Zoom pelo teclado |
| Page Up / Page Down | Rolar barra lateral |

---

## Índice da documentação

| Arquivo | Conteúdo |
|---|---|
| [`01_conceitos_aed2.md`](./01_conceitos_aed2.md) | Conteúdos de AED2 aplicados no projeto |
| [`02_arquitetura.md`](./02_arquitetura.md) | Arquitetura, módulos e diagramas de fluxo |
| [`03_estruturas_de_dados.md`](./03_estruturas_de_dados.md) | Estruturas internas: Grafo, Vértice, lista de adjacência |
| [`04_algoritmo_dijkstra.md`](./04_algoritmo_dijkstra.md) | Implementação, fluxograma e análise do Dijkstra |
| [`05_complexidade.md`](./05_complexidade.md) | Análise assintótica e gráficos comparativos |
| [`06_requisitos.md`](./06_requisitos.md) | Requisitos funcionais, não-funcionais e formatos de entrada |

---

## Referências

- CORMEN, T. H. et al. *Introdução a Algoritmos*. 3. ed. MIT Press, 2009.
- SEDGEWICK, R.; WAYNE, K. *Algorithms*. 4. ed. Addison-Wesley, 2011.
- OpenStreetMap Foundation. *OSM XML Format*. https://wiki.openstreetmap.org/wiki/OSM_XML
- Python Software Foundation. *heapq*. https://docs.python.org/3/library/heapq.html
- Pygame Community. *Pygame Docs*. https://www.pygame.org/docs/