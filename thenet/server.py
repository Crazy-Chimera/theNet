"""Minimal standard-library HTTP runtime for theNet."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlparse

from src.genesis import create_genesis
from src.relation import create_relation
from thenet.engine import build_closure

UI_ROOT = Path(__file__).resolve().parents[1] / "ui"
_STATE_LOCK = Lock()
_STATE: dict[str, list[dict[str, Any]]] = {
    "genesis": [],
    "relations": [],
    "closures": [],
    "events": [],
}


def _event(kind: str, message: str) -> dict[str, str]:
    return {"kind": kind, "message": message}


class RuntimeHandler(BaseHTTPRequestHandler):
    """Expose theNet engine and browser UI through one public HTTP boundary."""

    server_version = "theNet/0.1"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path == "/health":
            self._json(HTTPStatus.OK, {"status": "ready", "version": "0.1.0"})
            return

        if path == "/v1/state":
            self._json(HTTPStatus.OK, self._state_snapshot())
            return

        if path == "/":
            self._static("index.html")
            return

        if path in {"/app.js", "/styles.css"}:
            self._static(path.lstrip("/"))
            return

        self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        routes = {
            "/v1/genesis": self._create_genesis,
            "/v1/relations": self._create_relation,
            "/v1/closure": self._build_closure,
        }
        path = urlparse(self.path).path
        handler = routes.get(path)
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
            self._json(
                HTTPStatus.BAD_REQUEST,
                {"error": f"invalid request: {exc}"},
            )

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _create_genesis(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = asdict(
            create_genesis(
                subject=self._required_string(payload, "subject"),
                created_at=self._required_string(payload, "created_at"),
            )
        )
        with _STATE_LOCK:
            _STATE["genesis"].append(result)
            _STATE["events"].insert(0, _event("GENESIS", f"Created {result['subject']}"))
        return result

    def _create_relation(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = asdict(
            create_relation(
                source_id=self._required_string(payload, "source_id"),
                target_id=self._required_string(payload, "target_id"),
                kind=self._required_string(payload, "kind"),
                created_at=self._required_string(payload, "created_at"),
            )
        )
        result["relations"] = list(result["relations"]) if "relations" in result else []
        with _STATE_LOCK:
            _STATE["relations"].append(result)
            _STATE["events"].insert(0, _event("RELATION", f"Created {result['kind']} relation"))
        return result

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
        result = asdict(closure)
        with _STATE_LOCK:
            _STATE["closures"].append(result)
            _STATE["events"].insert(
                0,
                _event(
                    "AGENT_OMEGA",
                    f"Genesis Closure committed: {closure.agent_state.id}",
                ),
            )
        return result

    def _state_snapshot(self) -> dict[str, Any]:
        with _STATE_LOCK:
            return {
                "genesis": list(_STATE["genesis"]),
                "relations": list(_STATE["relations"]),
                "closures": list(_STATE["closures"]),
                "events": list(_STATE["events"]),
            }

    def _static(self, name: str) -> None:
        path = (UI_ROOT / name).resolve()
        if UI_ROOT.resolve() not in path.parents:
            self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})
            return

        try:
            body = path.read_bytes()
        except FileNotFoundError:
            self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})
            return

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
        }.get(path.suffix, "application/octet-stream")

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

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
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
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
