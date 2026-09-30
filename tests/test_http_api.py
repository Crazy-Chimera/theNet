"""Integration tests for the live-shaped theNet HTTP API."""

from __future__ import annotations

import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from thenet.server import RuntimeHandler, ThreadingHTTPServer


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def request_json(server, path: str, payload: object):
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        f"http://127.0.0.1:{server.server_port}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = urlopen(request)
        return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=2)
    server.server_close()


def test_http_genesis_api_persists_runtime_state():
    server, thread = start_server()
    try:
        status, payload = request_json(
            server,
            "/v1/genesis",
            {"subject": "alpha", "created_at": "2026-09-30T00:00:00Z"},
        )
        assert status == 200
        assert payload["subject"] == "alpha"

        with urlopen(f"http://127.0.0.1:{server.server_port}/v1/state") as response:
            state = json.load(response)
        assert state["genesis"][-1]["id"] == payload["id"]
        assert state["events"][0]["kind"] == "GENESIS"
    finally:
        stop_server(server, thread)


def test_http_relation_api_persists_runtime_state():
    server, thread = start_server()
    try:
        status, payload = request_json(
            server,
            "/v1/relations",
            {
                "source_id": "alpha",
                "target_id": "beta",
                "kind": "supports",
                "created_at": "2026-09-30T00:00:00Z",
            },
        )
        assert status == 200
        assert payload["kind"] == "supports"

        with urlopen(f"http://127.0.0.1:{server.server_port}/v1/state") as response:
            state = json.load(response)
        assert state["relations"][-1]["id"] == payload["id"]
    finally:
        stop_server(server, thread)


def test_http_closure_api_exposes_and_persists_agent_omega_closure():
    server, thread = start_server()
    try:
        status, payload = request_json(
            server,
            "/v1/closure",
            {
                "source_subject": "alpha",
                "target_subject": "beta",
                "relation_kind": "supports",
                "proposal_text": "test proposal",
                "evidence": "test evidence",
                "expression_id": "expr-1",
                "created_at": "2026-09-30T00:00:00Z",
            },
        )
        assert status == 200
        for key in (
            "source", "target", "relation", "phi", "omega", "omega2",
            "resonance", "proposal", "verification", "gamma", "pi",
            "psi", "theta", "rho", "sigma", "iota", "agent_state",
        ):
            assert key in payload

        with urlopen(f"http://127.0.0.1:{server.server_port}/v1/state") as response:
            state = json.load(response)
        assert state["closures"][-1]["iota"]["id"] == payload["iota"]["id"]
        assert state["events"][0]["kind"] == "AGENT_OMEGA"
    finally:
        stop_server(server, thread)


def test_http_api_rejects_invalid_json():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/genesis",
            data=b"{",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(request)
        except HTTPError as error:
            assert error.code == 400
            assert json.load(error) == {"error": "request body must be valid JSON"}
        else:
            raise AssertionError("invalid JSON was accepted")
    finally:
        stop_server(server, thread)


def test_http_api_rejects_missing_fields():
    server, thread = start_server()
    try:
        status, payload = request_json(server, "/v1/genesis", {"subject": "alpha"})
        assert status == 400
        assert payload == {"error": "created_at must be non-empty"}
    finally:
        stop_server(server, thread)


def test_http_api_requires_json_content_type():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/genesis",
            data=b'{"subject":"alpha","created_at":"now"}',
            method="POST",
        )
        try:
            urlopen(request)
        except HTTPError as error:
            assert error.code == 400
            assert json.load(error) == {"error": "Content-Type must be application/json"}
        else:
            raise AssertionError("non-JSON request was accepted")
    finally:
        stop_server(server, thread)


def test_http_api_unknown_route():
    server, thread = start_server()
    try:
        status, payload = request_json(server, "/v1/unknown", {})
        assert status == 404
        assert payload == {"status": "not_found"}
    finally:
        stop_server(server, thread)
