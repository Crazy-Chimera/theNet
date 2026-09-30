import json
import threading
from http.client import HTTPConnection
import pytest

from thenet.server import RuntimeHandler, ThreadingHTTPServer, runtime_port


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_health_endpoint_is_ready():
    server, thread = start_server()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/health")
        response = connection.getresponse()
        payload = json.loads(response.read())
        assert response.status == 200
        assert payload["status"] == "ready"
        assert payload["version"] == "3.0.0-mvp"
    finally:
        stop_server(server, thread)


def test_root_endpoint_serves_public_ui():
    server, thread = start_server()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        assert response.status == 200
        assert response.getheader("Content-Type").startswith("text/html")
        assert "theNet 3.0 MVP" in body
        assert "closure-form" in body
    finally:
        stop_server(server, thread)


def test_state_endpoint_returns_runtime_collections():
    server, thread = start_server()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/v1/state")
        response = connection.getresponse()
        payload = json.loads(response.read())
        assert response.status == 200
        assert set(payload) == {"genesis", "relations", "closures", "events"}
    finally:
        stop_server(server, thread)


def test_unknown_path_returns_not_found():
    server, thread = start_server()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/unknown")
        response = connection.getresponse()
        assert response.status == 404
        assert json.loads(response.read()) == {"status": "not_found"}
    finally:
        stop_server(server, thread)


def test_runtime_port_rejects_invalid_values(monkeypatch):
    monkeypatch.setenv("PORT", "invalid")
    with pytest.raises(ValueError, match="integer"):
        runtime_port()


@pytest.mark.parametrize("value", ["0", "65536"])
def test_runtime_port_rejects_out_of_range(monkeypatch, value):
    monkeypatch.setenv("PORT", value)
    with pytest.raises(ValueError, match="between"):
        runtime_port()
