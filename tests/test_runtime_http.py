import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest

from thenet.server import RuntimeHandler, runtime_port


def test_health_endpoint_is_ready():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/health")
        response = connection.getresponse()

        assert response.status == 200
        assert json.loads(response.read()) == {"status": "ready"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_root_endpoint_identifies_runtime():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/")
        response = connection.getresponse()

        assert response.status == 200
        assert json.loads(response.read()) == {
            "service": "theNet",
            "status": "ready",
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_unknown_path_returns_not_found():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("GET", "/unknown")
        response = connection.getresponse()

        assert response.status == 404
        assert json.loads(response.read()) == {"status": "not_found"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_runtime_port_rejects_invalid_values(monkeypatch):
    monkeypatch.setenv("PORT", "invalid")

    with pytest.raises(ValueError, match="integer"):
        runtime_port()


@pytest.mark.parametrize("value", ["0", "65536"])
def test_runtime_port_rejects_out_of_range(monkeypatch, value):
    monkeypatch.setenv("PORT", value)

    with pytest.raises(ValueError, match="between"):
        runtime_port()
