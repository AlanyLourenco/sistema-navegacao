"""
Servidor de clipboard para o NavGrafo rodando em Docker.

Recebe imagens PNG do container e as coloca automaticamente
na area de transferencia do macOS via osascript.

Uso:
    python3 mac_clip_server.py

Deixe rodando enquanto usar o app no Docker.
"""
import os
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 9999


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/copy':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)

        fd, tmp = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        try:
            with open(tmp, 'wb') as f:
                f.write(data)
            result = subprocess.run(
                ['osascript', '-e',
                 f'set the clipboard to (read (POSIX file "{tmp}") as «class PNGf»)'],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                print('✓ Imagem copiada para a área de transferência')
                self.send_response(200)
            else:
                err = result.stderr.decode().strip()
                print(f'✗ osascript falhou: {err}')
                self.send_response(500)
        except Exception as e:
            print(f'✗ Erro: {e}')
            self.send_response(500)
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass
        self.end_headers()

    def log_message(self, *args):
        pass  # silencia logs HTTP do servidor


print(f'NavGrafo Clipboard Server — porta {PORT}')
print('Deixe aberto enquanto usar o app no Docker.')
print('Ctrl+C para encerrar.\n')
try:
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
except KeyboardInterrupt:
    print('\nEncerrado.')
    sys.exit(0)
