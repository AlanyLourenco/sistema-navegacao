# Sistema de Navegação (NavGrafo UFG)

Projeto acadêmico que implementa um sistema de navegação baseado em grafos. Fornece ferramentas para importar mapas reais, construir grafos (vértices e arestas), editar grafos por interação (adicionar/remover vértices e arestas), e calcular o menor caminho entre dois pontos usando Dijkstra.

Principais objetivos:
- Importar mapas em vários formatos (.poly, .osm/.xml, .txt/.csv) e converter em grafos.
- Numerar vértices e exibir pesos das arestas (distâncias reais).
- Calcular e destacar o menor caminho entre dois vértices.
- Permitir edição por clique (adicionar/remover vértices e arestas).
- Exibir estatísticas da execução do algoritmo (tempo, nós explorados, custo).
- Salvar/copiar imagem do grafo.

---

**Estrutura do repositório**

- `trabalho final/` : C sources usados para converter e gerar arquivos `.poly` e outra utilidades.
- `versao JavaScript/` : Versão em HTML/JS do visualizador (arquivos: `index.html`, `script.js`, `style.css`, `data.js`).
- `versao Python/` : Versão principal em Python com UI em Pygame. Contém:
	- `main.py` : Aplicação Pygame (UI, interação, renderização).
	- `core.py` : Modelo de grafo e loaders (importadores: `.poly`, `.txt`, `.osm`).
	- `algorithms.py` : Implementação de Dijkstra (retorna caminho, custo, nós explorados e tempo).
	- `gui.py` : Constantes de UI e utilitários de câmera e botões.
	- `README.md` : Documentação específica da versão Python.
	- Arquivos de dados: `Campus2UFG&Regiao.osm`, `Campus2UFG&Regiao.poly` (exemplos reais).

---

## Requisitos

- Python 3.8+ (para a versão Python)
- Pygame: `pip install pygame`
- (Opcional, para copiar imagem ao clipboard no Windows) `pywin32` e `Pillow` — o projeto tenta usar a API nativa do Windows; se não estiver disponível, faz fallback salvando PNG.
- Navegador moderno (para a versão JavaScript)
- Compilador C (gcc/clang) se quiser compilar os arquivos em `trabalho final/`.

## Como executar

Versão Python (UI com Pygame):

1. Instale dependências:

```bash
pip install pygame
```

2. Execute:

```bash
python "versao Python/main.py"
```

Opcionalmente passe um arquivo de mapa como argumento:

```bash
python "versao Python/main.py" "trabalho final/Campus2UFG&Regiao.poly"
```

Versão JavaScript (visualizador leve):

1. Abra `versao JavaScript/index.html` em um navegador.

Versão C (conversores):

1. Entre em `trabalho final/` e compile os fontes conforme necessidade (ex.: `gcc`).

---

## Formatos de entrada suportados

- `.poly` — formato gerado por ferramentas de processamento de OSM.
- `.osm` / `.xml` — arquivos OSM com nós e ways (vias `highway`).
- `.txt` / `.csv` / `.tsv` / `.dat` — formato simples com seções `VERTICES` e `ARESTAS` (veja a `versao Python/README.md` para exemplo).

## Controles (versão Python)

- `O` : selecionar origem (clique no vértice)
- `D` : selecionar destino (clique no vértice)
- `C` : calcular menor caminho (Dijkstra)
- `P` : pan (mover mapa)
- `F` : ajustar mapa à tela (fit)
- `R` : limpar seleção
- `V` : adicionar vértice (clique)
- `A` : adicionar aresta (não-dirigida)
- `U` : adicionar aresta dirigida (única)
- `X` : deletar vértice (clique)
- `Z` : deletar aresta (clique na aresta)
- `N` : mostrar/ocultar IDs dos vértices
- `W` : mostrar/ocultar pesos das arestas
- `L` : importar mapa (abrir diálogo ou carregar primeiro mapa encontrado)
- `I` : copiar/salvar imagem do mapa (copia para clipboard no Windows quando possível)
- `Q` : sair

---

## Recursos e requisitos atendidos (RF)

- RF01: Importar mapas reais → implementado (`core.py` loaders).
- RF02: Enumerar vértices e exibir pesos → toggles N / W.
- RF04: Exibir menor caminho em cor diferenciada → Dijkstra + renderização em `main.py`.
- RF05: Edição por clique (adicionar/remover vértices/arestas) → modos na UI.
- RF07: Exibir estatísticas do algoritmo (tempo, nós explorados, custo) → painel lateral.
- RF08: Copiar imagem → tecla `I`; implementação tenta enviar imagem ao clipboard no Windows, com fallback para salvar arquivo PNG.

---

## Desenvolvimento

- Arquitetura: `core.py` contém modelo e IO; `main.py` contém UI/controle; `algorithms.py` contém algoritmos.
- Para contribuições, prefira alterações pequenas e testáveis; mantenha `core.py` desacoplado de Pygame para facilitar testes.

## Testes manuais recomendados

- Rodar `versao Python/main.py`, carregar o mapa de exemplo, selecionar origem/destino e pressionar `C`.
- Testar adição e remoção de arestas e vértices nos modos apropriados.
- Pressionar `I` e colar em Paint para validar a cópia para clipboard no Windows.

