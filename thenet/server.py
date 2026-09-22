"""Minimal standard-library HTTP runtime for deployment health checks."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class RuntimeHandler(BaseHTTPRequestHandler):
    """Serve only the public runtime health boundary."""

    server_version = "theNet/0.1"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"status": "ready"})
            return

        if self.path == "/":
            self._json(HTTPStatus.OK, {"service": "theNet", "status": "ready"})
            return

        self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, status: HTTPStatus, payload: dict[str, str]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def runtime_port() -> int:
    raw = os.getenv("PORT", "8000")
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError("PORT must be an integer") from exc

    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")

    return port


def serve() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", runtime_port()), RuntimeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
