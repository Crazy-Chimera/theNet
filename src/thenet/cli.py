"""Minimal HTTP runtime for theNet."""

from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from thenet.persistence import run_persistence_probe


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args: object) -> None:
        return


def main() -> None:
    if os.getenv("THENET_PERSISTENCE_PROBE", "0") == "1":
        print(run_persistence_probe(), flush=True)

    port = int(os.getenv("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
