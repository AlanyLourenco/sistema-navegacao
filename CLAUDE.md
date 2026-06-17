# NavGrafo UFG — Sistema de Navegação em Grafos

Sistema de visualização e roteamento em grafos do campus UFG. AED2 2026-1.

## Stack
- Python 3.8+ / Pygame 2.x
- Algoritmo: Dijkstra com min-heap (`heapq`)
- Formatos de mapa: `.poly`, `.osm`/`.xml`, `.txt`/`.csv`/`.tsv`

## Estrutura

```
sistema-navegacao/
├── Dockerfile                    # Imagem Docker (X11 + xclip)
├── Campus2UFG&Regiao.osm         # Mapa OSM do campus UFG
├── Campus2UFG&Regiao.poly        # Mesmo mapa em formato .poly
└── versao Python/
    ├── main.py        # Aplicação principal (App, loop, eventos, câmera)
    ├── gui.py         # Constantes visuais, Camera, Botao
    ├── core.py        # Grafo, Vertice, carregadores de mapa
    ├── algorithms.py  # dijkstra()
    └── nav_grafo_ufg.py  # Launcher de compatibilidade
```

## Como rodar

### Local
```bash
cd "versao Python"
pip install pygame
python main.py ../Campus2UFG\&Regiao.osm
```

### Docker (requer X11)

```bash
# Build
docker build -t navgrafo-ufg .

# Linux
xhost +local:docker
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix navgrafo-ufg

# macOS (XQuartz instalado)
xhost + localhost
docker run --rm -e DISPLAY=host.docker.internal:0 navgrafo-ufg
```

## Módulos principais

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | `App`: loop principal, eventos, modos de edição, `copiar_imagem` |
| `gui.py` | `Camera` (mundo↔tela, zoom, fit), `Botao`, paleta de cores |
| `core.py` | `Grafo`, `Vertice`, parsers `.poly`/`.txt`/`.osm` |
| `algorithms.py` | `dijkstra(grafo, inicio, fim)` → `(caminho, dist, explorados, tempo_ms)` |

## Clipboard (`copiar_imagem`)

- **Windows**: salva PNG em arquivo temporário e invoca PowerShell (`System.Windows.Forms.Clipboard::SetImage`) — compatível com Win+V e qualquer app
- **macOS**: `osascript` com `«class PNGf»`
- **Linux/Docker**: `xclip -selection clipboard -t image/png`
- Fallback: salva `grafo_<numero>.png` no diretório atual

> A abordagem anterior no Windows usava `ctypes.windll` (CF_DIB manual via `GlobalAlloc`/`SetClipboardData`), que truncava ponteiros de 64 bits e não registrava os formatos esperados pelo histórico de área de transferência.
