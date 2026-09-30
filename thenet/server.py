"""Minimal standard-library HTTP runtime for theNet."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from src.genesis import create_genesis
from src.relation import create_relation
from thenet.engine import build_closure


class RuntimeHandler(BaseHTTPRequestHandler):
    """Expose theNet's deterministic engine through a small HTTP boundary."""

    server_version = "theNet/0.2"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"status": "ready"})
            return

        if self.path == "/":
            self._json(HTTPStatus.OK, {"service": "theNet", "status": "ready"})
            return

        self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        routes = {
            "/v1/genesis": self._create_genesis,
            "/v1/relations": self._create_relation,
            "/v1/closure": self._build_closure,
        }
        handler = routes.get(self.path)
        if handler is None:
            self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})
            return

        try:
            payload = self._read_json()
            result = handler(payload)
            self._json(HTTPStatus.OK, result)
        except ValueError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except (TypeError, KeyError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": f"invalid request: {exc}"})

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _create_genesis(self, payload: dict[str, Any]) -> dict[str, Any]:
        return asdict(
            create_genesis(
                subject=self._required_string(payload, "subject"),
                created_at=self._required_string(payload, "created_at"),
            )
        )

    def _create_relation(self, payload: dict[str, Any]) -> dict[str, Any]:
        return asdict(
            create_relation(
                source_id=self._required_string(payload, "source_id"),
                target_id=self._required_string(payload, "target_id"),
                kind=self._required_string(payload, "kind"),
                created_at=self._required_string(payload, "created_at"),
            )
        )

    def _build_closure(self, payload: dict[str, Any]) -> dict[str, Any]:
        closure = build_closure(
            source_subject=self._required_string(payload, "source_subject"),
            target_subject=self._required_string(payload, "target_subject"),
            relation_kind=self._required_string(payload, "relation_kind"),
            proposal_text=self._required_string(payload, "proposal_text"),
            evidence=self._required_string(payload, "evidence"),
            expression_id=self._required_string(payload, "expression_id"),
            created_at=self._required_string(payload, "created_at"),
        )
        return asdict(closure)

    def _read_json(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            raise ValueError("Content-Type must be application/json")

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValueError("Content-Length is required")

        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("Content-Length must be an integer") from exc

        if length <= 0:
            raise ValueError("request body must not be empty")

        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            raise ValueError("request body must be valid JSON") from exc

        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")

        return payload

    @staticmethod
    def _required_string(payload: dict[str, Any], name: str) -> str:
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")
        return value

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
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
