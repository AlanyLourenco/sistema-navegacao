"""
Cross-platform clipboard server for NavGrafo.

Listens on port 9999 and accepts POST /copy with PNG bytes in the request body.
- macOS: uses `osascript` (same approach as mac_clip_server.py)
- Windows: uses Pillow + ctypes to place CF_DIB data on the clipboard
- Other: saves a temporary file and prints its path

Run on the host (not inside the container):
    python clip_server.py

From inside the container the app can POST the PNG to http://host.docker.internal:9999/copy
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import platform
import subprocess
import tempfile
import os
import sys
from io import BytesIO

PORT = 9999

SYSTEM = platform.system()

# Windows clipboard helpers using ctypes
if SYSTEM == "Windows":
    import ctypes
    from ctypes import wintypes
    from PIL import Image

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    CF_DIB = 8
    GHND = 0x0042  # GMEM_MOVEABLE | GMEM_ZEROINIT

    def copy_png_to_clipboard_windows(png_bytes: bytes) -> bool:
        try:
            img = Image.open(BytesIO(png_bytes)).convert("RGBA")
            bmp_io = BytesIO()
            img.save(bmp_io, format="BMP")
            bmp_data = bmp_io.getvalue()
            dib = bmp_data[14:]
            size = len(dib)

            h_mem = kernel32.GlobalAlloc(GHND, size)
            if not h_mem:
                return False
            lp_mem = kernel32.GlobalLock(h_mem)
            if not lp_mem:
                kernel32.GlobalFree(h_mem)
                return False
            # copy memory
            ctypes.memmove(lp_mem, dib, size)
            kernel32.GlobalUnlock(h_mem)

            if not user32.OpenClipboard(None):
                kernel32.GlobalFree(h_mem)
                return False
            try:
                user32.EmptyClipboard()
                if not user32.SetClipboardData(CF_DIB, h_mem):
                    # If SetClipboardData fails, free memory
                    kernel32.GlobalFree(h_mem)
                    return False
            finally:
                user32.CloseClipboard()
            return True
        except Exception as e:
            print(f"Windows clipboard error: {e}")
            return False

# macOS helper uses osascript like before
elif SYSTEM == "Darwin":
    def copy_png_to_clipboard_mac(png_bytes: bytes) -> bool:
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            with open(tmp, "wb") as f:
                f.write(png_bytes)
            result = subprocess.run(
                ["osascript", "-e", f'set the clipboard to (read (POSIX file "{tmp}") as «class PNGf»)'],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"macOS clipboard error: {e}")
            return False
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

else:
    def copy_png_to_clipboard_other(png_bytes: bytes) -> bool:
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        with open(tmp, "wb") as f:
            f.write(png_bytes)
        print("Saved image to", tmp)
        return True


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/copy':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)

        ok = False
        if SYSTEM == 'Darwin':
            ok = copy_png_to_clipboard_mac(data)
        elif SYSTEM == 'Windows':
            ok = copy_png_to_clipboard_windows(data)
        else:
            ok = copy_png_to_clipboard_other(data)

        if ok:
            self.send_response(200)
        else:
            self.send_response(500)
        self.end_headers()

    def log_message(self, *args):
        pass


def main():
    print(f'NavGrafo Clipboard Server — porta {PORT} (host OS: {SYSTEM})')
    print('Deixe aberto enquanto usar o app no Docker.')
    print('Ctrl+C para encerrar.\n')
    try:
        HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nEncerrado.')
        sys.exit(0)


if __name__ == '__main__':
    main()
