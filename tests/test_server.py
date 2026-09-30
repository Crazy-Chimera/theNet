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


def test_control_room_replay_is_deterministic():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/replay",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            assert payload["deterministic"] is True
            assert payload["graph_match"] is True
            assert payload["run_match"] is True
            assert payload["artifact_match"] is True
            assert payload["original_cycles"] == 3
            assert payload["replay_cycles"] == 3
            assert payload["original_graph_id"] == payload["replay_graph_id"]
            assert payload["first_divergence_cycle"] is None
            assert payload["first_divergence_artifact"] is None
            assert len(payload["artifact_comparisons"]) == 30
            assert all(item["match"] is True for item in payload["artifact_comparisons"])
    finally:
        stop_server(server, thread)


def test_control_room_counterfactual_replay_diverges_at_selected_cycle():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/counterfactual",
            data=json.dumps({
                "cycle_index": 2,
                "proposal_text": "counterfactual hypothesis",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            assert payload["cycle_index"] == 2
            assert payload["baseline_cycles"] == 3
            assert payload["counterfactual_cycles"] == 3
            assert payload["diverged"] is True
            assert payload["replay"]["first_divergence_cycle"] == 2
            assert payload["replay"]["first_divergence_artifact"] == "proposal"
            assert all(
                item["match"]
                for item in payload["replay"]["artifact_comparisons"]
                if item["cycle_index"] == 1
            )
            assert any(
                not item["match"]
                for item in payload["replay"]["artifact_comparisons"]
                if item["cycle_index"] >= 2
            )
    finally:
        stop_server(server, thread)


def test_control_room_causal_trace_exposes_propagation():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/causal-trace",
            data=json.dumps({
                "cycle_index": 2,
                "proposal_text": "counterfactual hypothesis",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            assert payload["trace"]["first_divergence_cycle"] == 2
            assert payload["trace"]["first_divergence_artifact"] == "proposal"
            assert payload["trace"]["propagation_cycles"] == [2, 3]
            assert "C2:proposal" in payload["trace"]["changed_artifacts"]
            assert any(
                step["relation"] == "informs_next_proposal" and step["changed"]
                for step in payload["trace"]["steps"]
            )
    finally:
        stop_server(server)



def test_control_room_state_diff_exposes_metric_and_resource_changes():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/state-diff",
            data=json.dumps({
                "cycle_index": 2,
                "proposal_text": "counterfactual hypothesis",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            diff = payload["state_diff"]
            assert diff["first_divergence_cycle"] == 2
            assert diff["changed_field_count"] > 0
            assert diff["propagation_cycles"] == [2, 3]
            assert any(
                item["scope"] == "metrics" and item["changed"]
                for item in diff["fields"]
            )
            assert any(
                item["scope"] == "state" and item["field"] == "singularity_id" and item["changed"]
                for item in diff["fields"]
            )
    finally:
        stop_server(server)



def test_control_room_impact_vector_exposes_branch_deltas():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/impact-vector",
            data=json.dumps({
                "cycle_index": 2,
                "proposal_text": "counterfactual hypothesis",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            impact = payload["impact_vector"]
            assert impact["first_divergence_cycle"] == 2
            assert len(impact["vectors"]) == 3
            assert impact["vectors"][0]["changed_fields"] == 0
            assert impact["vectors"][1]["changed_fields"] > 0
            assert impact["vectors"][2]["changed_fields"] > 0
    finally:
        stop_server(server)



def test_control_room_experiment_matrix_exposes_independent_cases():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/experiment-matrix",
            data=json.dumps({
                "cases": [
                    {"id": "a", "cycle_index": 2, "proposal_text": "alternative A"},
                    {"id": "b", "cycle_index": 3, "proposal_text": "alternative B"},
                ],
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            matrix = payload["matrix"]
            assert matrix["case_count"] == 2
            assert [case["case"]["id"] for case in matrix["cases"]] == ["a", "b"]
            assert matrix["cases"][0]["impact_vector"]["first_divergence_cycle"] == 2
            assert matrix["cases"][1]["impact_vector"]["first_divergence_cycle"] == 3
    finally:
        stop_server(server)



def test_control_room_reproducibility_returns_fingerprints():
    server, thread = start_server()
    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/reproducibility",
            data=json.dumps({
                "cases": [
                    {"id": "a", "cycle_index": 2, "proposal_text": "alternative A"},
                    {"id": "b", "cycle_index": 3, "proposal_text": "alternative B"},
                ],
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            fingerprint = payload["fingerprint"]
            assert len(fingerprint["design_fingerprint"]) == 64
            assert len(fingerprint["result_fingerprint"]) == 64
            assert fingerprint["runtime_contract"] == "counterfactual-matrix-v1.7"
    finally:
        stop_server(server)



def test_control_room_query_traces_evidence_path():
    server, thread = start_server()
    try:
        demo_request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/demo",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(demo_request) as response:
            demo = json.load(response)

        source_id = demo["cycles"][1]["proposal_id"]
        target_id = demo["cycles"][1]["audit"]["memory_id"]
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/control/query",
            data=json.dumps({
                "operation": "path",
                "source_id": source_id,
                "target_id": target_id,
                "direction": "forward",
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            payload = json.load(response)
            assert response.status == 200
            assert payload["graph_id"] == demo["evidence_graph"]["id"]
            query = payload["query"]
            assert query["depth"] == 5
            assert [edge["relation"] for edge in query["edges"]] == [
                "verified_by_consensus",
                "converges",
                "authorizes_execution",
                "produces",
                "remembered_as",
            ]
    finally:
        stop_server(server, thread)


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
            shares = dict(payload["allocation"]["memory_by_cycle"])
            assert shares[2] > shares[1]
            graph = payload["evidence_graph"]
            assert graph["id"]
            assert graph["nodes"]
            assert graph["edges"]
            node_ids = {node["id"] for node in graph["nodes"]}
            audit = payload["cycles"][1]["audit"]
            assert audit["memory_id"] in node_ids
            assert audit["state_id"] in node_ids
            assert any(edge["relation"] == "remembered_as" for edge in graph["edges"])
            assert any(edge["relation"] == "informs" for edge in graph["edges"])
            assert audit["verification_ids"]
            for key in (
                "consensus_id", "convergence_id", "execution_id", "commit_id",
                "utility_id", "credit_id", "memory_id", "state_id",
                "memory_before_id", "memory_after_id", "compute_before_id", "compute_after_id",
            ):
                assert audit[key]
    finally:
        stop_server(server, thread)

