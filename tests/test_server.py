import json
import os
import threading
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from thenet.server import RuntimeHandler, ThreadingHTTPServer, runtime_port


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_runtime_health_endpoint():
    server, thread = start_server()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/health") as response:
            assert response.status == 200
            assert json.load(response) == {"status": "ready"}
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_runtime_root_endpoint():
    server, thread = start_server()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/") as response:
            assert response.status == 200
            assert json.load(response) == {"service": "theNet", "status": "ready"}
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_runtime_unknown_path_is_not_found():
    server, thread = start_server()
    try:
        with pytest.raises(HTTPError) as error:
            urlopen(f"http://127.0.0.1:{server.server_port}/unknown")
        assert error.value.code == 404
        assert json.load(error.value) == {"status": "not_found"}
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


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
