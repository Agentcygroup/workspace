#!/usr/bin/env python3
"""Serve the backend on localhost:8765 and the frontend at /."""
from __future__ import annotations
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from backend import make_server  # noqa: E402


FRONTEND = HERE / "frontend"
MIME = {".html": "text/html", ".css": "text/css", ".js": "application/javascript"}


class FrontendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            path = "/index.html"
        f = FRONTEND / path.lstrip("/")
        if not f.exists() or not f.is_file():
            self.send_response(404)
            self.end_headers()
            return
        body = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(f.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    api = make_server("127.0.0.1", 8765)
    ui = HTTPServer(("127.0.0.1", 8766), FrontendHandler)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    print("api      http://127.0.0.1:8765")
    print("frontend http://127.0.0.1:8766")
    try:
        ui.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
