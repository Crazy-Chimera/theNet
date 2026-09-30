import json
import threading
from urllib.request import Request, urlopen

from src.sqlite_store import SQLiteStore
from thenet.server import RuntimeHandler, ThreadingHTTPServer


def start_persistent_server(path):
    store = SQLiteStore(path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHandler, store=store)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=2)
    server.server_close()


def post(base_url, path, payload):
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.load(response)


def test_http_runtime_persists_core_entities_across_restart(tmp_path):
    path = tmp_path / "thenet.db"
    payload = {
        "subject": "persistent-agent",
        "created_at": "2026-09-30T00:00:00Z",
    }

    server, thread = start_persistent_server(path)
    try:
        status, created = post(
            f"http://127.0.0.1:{server.server_port}",
            "/v1/genesis",
            payload,
        )
        assert status == 200
        identifier = created["id"]
    finally:
        stop_server(server, thread)

    server, thread = start_persistent_server(path)
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/v1/state") as response:
            state = json.load(response)

        assert any(item["id"] == identifier for item in state["genesis"])
        assert any(
            item["subject"] == "persistent-agent"
            for item in state["genesis"]
        )
    finally:
        stop_server(server, thread)


def test_http_runtime_persists_relation(tmp_path):
    path = tmp_path / "thenet.db"
    payload = {
        "source_id": "agent:a",
        "target_id": "agent:b",
        "kind": "trust",
        "created_at": "2026-09-30T00:00:00Z",
    }

    server, thread = start_persistent_server(path)
    try:
        _, created = post(
            f"http://127.0.0.1:{server.server_port}",
            "/v1/relations",
            payload,
        )
        identifier = created["id"]
    finally:
        stop_server(server, thread)

    server, thread = start_persistent_server(path)
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/v1/state") as response:
            state = json.load(response)

        assert any(item["id"] == identifier for item in state["relations"])
    finally:
        stop_server(server, thread)
