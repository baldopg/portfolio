# Servidor local para desarrollo: sirve la carpeta del portfolio sin caché, para que el
# navegador siempre cargue la última versión de CSS, JS y GLB.
# Uso: python serve_nocache.py [puerto]
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # C:/Users/Baldo/Desktop/portfolio


class NoCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):   # silencioso: solo errores
        if not str(args[1] if len(args) > 1 else "").startswith(("2", "3")):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5173
    ThreadingHTTPServer(("127.0.0.1", port), partial(NoCache, directory=str(ROOT))).serve_forever()
