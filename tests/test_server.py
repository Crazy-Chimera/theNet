import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from thenet.server import RuntimeHandler, ThreadingHTTPServer, runtime_port


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=2)
    server.server_close()


def test_runtime_health_endpoint():
    server, thread = start_server()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/health") as response:
            assert response.status == 200
            assert json.load(response)["status"] == "ready"
    finally:
        stop_server(server, thread)


def test_runtime_root_serves_public_ui():
    server, thread = start_server()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/") as response:
            body = response.read().decode("utf-8")
            assert response.status == 200
            assert response.headers["Content-Type"].startswith("text/html")
            assert "theNet" in body
            assert "closure-form" in body
    finally:
        stop_server(server, thread)


def test_runtime_state_endpoint():
    server, thread = start_server()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/v1/state") as response:
            payload = json.load(response)
            assert response.status == 200
            assert set(payload) == {"genesis", "relations", "closures", "events"}
    finally:
        stop_server(server, thread)


def test_runtime_unknown_path_is_not_found():
    server, thread = start_server()
    try:
        with pytest.raises(HTTPError) as error:
            urlopen(f"http://127.0.0.1:{server.server_port}/unknown")
        assert error.value.code == 404
        assert json.load(error.value) == {"status": "not_found"}
    finally:
        stop_server(server, thread)


@pytest.mark.parametrize("value", ["0", "65536", "not-a-port"])
def test_runtime_port_rejects_invalid_values(monkeypatch, value):
    monkeypatch.setenv("PORT", value)
    with pytest.raises(ValueError):
        runtime_port()


def test_runtime_port_defaults(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert runtime_port() == 8000


def test_runtime_port_accepts_valid_value(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    assert runtime_port() == 8080

def test_control_room_demo_exposes_recursive_f10_feedback():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/demo",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            assert payload["cycle_count"] == 3
            assert payload["all_converged"] is True
            assert payload["state_versions"] == [2, 3, 4]
            assert payload["cycles"][1]["learning"]["memory_dependency"] is True
            assert payload["cycles"][1]["learning"]["verified_improvement"] is True
            assert payload["allocation"]["improvement_bonus"] == 0.25
            assert payload["allocation"]["memory_by_cycle"][1][1] > 50.0
    finally:
        stop_server(server, thread)

