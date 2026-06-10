"""Compatibilidade com a estrutura antiga.

1. Para que serve o arquivo:
    - Script de compatibilidade para quem estiver habituado a executar
      `nav_grafo_ufg.py`; simplesmente delega para `main.App`.

2. Como funciona:
    - Importa `App` de `main` e executa `App().run()` quando executado como
      script principal.

3. Quais requisitos atende:
    - Auxílio a usabilidade/habituais, mantendo histórico de execução simples.
"""

from main import App


if __name__ == '__main__':
    App().run()
