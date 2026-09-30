"""Minimal standard-library HTTP runtime for theNet."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer as _ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlparse

from src.genesis import create_genesis
from src.genesis_population import create_genesis_population
from src.resource_state import create_resource_state
from src.evidence_graph import build_evidence_graph
from src.evidence_query import query_evidence_graph, trace_evidence_path
from src.replay import compare_recursive_replay
from src.counterfactual_replay import CounterfactualSpec, run_counterfactual
from src.causal_trace import build_causal_trace
from src.counterfactual_state_diff import build_counterfactual_state_diff
from src.counterfactual_impact_vector import build_counterfactual_impact_vector
from src.counterfactual_experiment_matrix import ExperimentCase, run_counterfactual_experiment_matrix
from src.counterfactual_reproducibility import fingerprint_experiment_matrix
from src.experiment_ledger import create_experiment_ledger_record
from src.postgres_store import PostgresStore
from src.relation import create_relation
from src.sqlite_store import SQLiteStore
from thenet.engine import build_closure, run_recursive_convergence_mvp

UI_ROOT = Path(__file__).resolve().parents[1] / "ui"
_STATE_LOCK = Lock()
_STATE: dict[str, list[dict[str, Any]]] = {
    "closures": [],
    "events": [],
}


def create_runtime_store():
    """Select durable PostgreSQL when configured, otherwise local SQLite."""
    dsn = os.getenv("DATABASE_URL") or os.getenv("THENET_POSTGRES_DSN")
    if dsn:
        return PostgresStore(dsn)

    return SQLiteStore(os.getenv("THENET_SQLITE_PATH", ":memory:"))


class ThreadingHTTPServer(_ThreadingHTTPServer):
    """HTTP server with one process-wide persistence boundary."""

    def __init__(self, server_address, RequestHandlerClass, store=None):
        super().__init__(server_address, RequestHandlerClass)
        self.store = store or create_runtime_store()

    def server_close(self) -> None:
        try:
            self.store.close()
        finally:
            super().server_close()


class RuntimeHandler(BaseHTTPRequestHandler):
    """Expose theNet engine and browser UI through one public HTTP boundary."""

    server_version = "theNet/0.1"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path == "/health":
            self._json(HTTPStatus.OK, {"status": "ready", "version": "0.1.0"})
            return

        if path == "/v1/control/ledger":
            with _STATE_LOCK:
                records = self.server.store.list_experiment_ledger()
            self._json(HTTPStatus.OK, {"records": list(records)})
            return

        if path.startswith("/v1/control/ledger/"):
            record_id = path.rsplit("/", 1)[-1]
            with _STATE_LOCK:
                record = self.server.store.get_experiment_ledger(record_id)
            if record is None:
                self._json(HTTPStatus.NOT_FOUND, {"status": "not_found"})
            else:
                self._json(HTTPStatus.OK, record)
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
            "/v1/control/demo": self._control_demo,
            "/v1/control/query": self._control_query,
            "/v1/control/replay": self._control_replay,
            "/v1/control/counterfactual": self._control_counterfactual,
            "/v1/control/causal-trace": self._control_causal_trace,
            "/v1/control/state-diff": self._control_state_diff,
            "/v1/control/impact-vector": self._control_impact_vector,
            "/v1/control/experiment-matrix": self._control_experiment_matrix,
            "/v1/control/reproducibility": self._control_reproducibility,
            "/v1/control/ledger": self._control_ledger,
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
        result = create_genesis(
            subject=self._required_string(payload, "subject"),
            created_at=self._required_string(payload, "created_at"),
        )
        with _STATE_LOCK:
            self.server.store.save_genesis(result)
        serialized = asdict(result)
        serialized["relations"] = list(serialized["relations"])
        with _STATE_LOCK:
            _STATE["events"].insert(0, self._event("GENESIS", f"Created {result.subject}"))
        return serialized

    def _create_relation(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = create_relation(
            source_id=self._required_string(payload, "source_id"),
            target_id=self._required_string(payload, "target_id"),
            kind=self._required_string(payload, "kind"),
            created_at=self._required_string(payload, "created_at"),
        )
        with _STATE_LOCK:
            self.server.store.save_relation(result)
        serialized = asdict(result)
        with _STATE_LOCK:
            _STATE["events"].insert(0, self._event("RELATION", f"Created {result.kind} relation"))
        return serialized

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
        with _STATE_LOCK:
            self.server.store.save_genesis(closure.source)
            self.server.store.save_genesis(closure.target)
            self.server.store.save_relation(closure.relation)
        result = asdict(closure)
        with _STATE_LOCK:
            _STATE["closures"].append(result)
            _STATE["events"].insert(
                0,
                self._event(
                    "AGENT_OMEGA",
                    f"Genesis Closure committed: {closure.agent_state.id}",
                ),
            )
        return result


    def _control_run(self, proposal_overrides=None):
        population = create_genesis_population(3, "2026-09-30T00:00:00Z")
        initial = population.agents[0]
        memory = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
        compute = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
        return run_recursive_convergence_mvp(
            population=population,
            initial_state=initial,
            proposal_builder=lambda index, state, previous: (
                proposal_overrides.get(index)
                if proposal_overrides and index in proposal_overrides
                else (
                    "observe initial state" if previous is None
                    else f"refine from memory {previous.result.memory.id}"
                )
            ),
            executor=lambda proposal: f"executed:{proposal.proposal}",
            quorum=2,
            new_singularity_builder=lambda index, proposal: f"control-room:{index}:{proposal.id}",
            created_at=("2026-09-30T00:00:01Z", "2026-09-30T00:00:02Z", "2026-09-30T00:00:03Z"),
            memory_resource=memory,
            compute_resource=compute,
            adaptive_memory_capacity=100.0,
            adaptive_compute_capacity=100.0,
            utility_builder=lambda index, previous: min(float(index) / 2.0, 1.0),
        )

    def _control_state_diff(self, payload: dict[str, Any]) -> dict[str, Any]:
        cycle_index = payload.get("cycle_index")
        if isinstance(cycle_index, bool) or not isinstance(cycle_index, int):
            raise ValueError("cycle_index must be an integer")
        proposal_text = self._required_string(payload, "proposal_text")
        baseline = self._control_run()
        spec = CounterfactualSpec(cycle_index=cycle_index, proposal_text=proposal_text)
        counterfactual, comparison = run_counterfactual(
            baseline=baseline,
            spec=spec,
            runner=lambda overrides: self._control_run(overrides),
        )
        diff = build_counterfactual_state_diff(comparison, baseline, counterfactual)
        return {
            "comparison": comparison.as_dict(),
            "state_diff": diff.as_dict(),
            "counterfactual_state_versions": list(counterfactual.state_versions),
        }


    def _control_impact_vector(self, payload: dict[str, Any]) -> dict[str, Any]:
        cycle_index = payload.get("cycle_index")
        if isinstance(cycle_index, bool) or not isinstance(cycle_index, int):
            raise ValueError("cycle_index must be an integer")
        proposal_text = self._required_string(payload, "proposal_text")
        baseline = self._control_run()
        spec = CounterfactualSpec(cycle_index=cycle_index, proposal_text=proposal_text)
        counterfactual, comparison = run_counterfactual(
            baseline=baseline,
            spec=spec,
            runner=lambda overrides: self._control_run(overrides),
        )
        state_diff = build_counterfactual_state_diff(comparison, baseline, counterfactual)
        impact = build_counterfactual_impact_vector(
            comparison, baseline, counterfactual, state_diff
        )
        return {
            "comparison": comparison.as_dict(),
            "state_diff": state_diff.as_dict(),
            "impact_vector": impact.as_dict(),
        }

    def _control_experiment_matrix(self, payload: dict[str, Any]) -> dict[str, Any]:
        baseline = self._control_run()
        raw_cases = payload.get("cases")
        if not isinstance(raw_cases, list) or not raw_cases:
            raise ValueError("cases must be a non-empty list")
        cases = []
        for raw in raw_cases:
            if not isinstance(raw, dict):
                raise ValueError("each case must be an object")
            case_id = self._required_string(raw, "id")
            cycle_index = raw.get("cycle_index")
            if isinstance(cycle_index, bool) or not isinstance(cycle_index, int):
                raise ValueError("case cycle_index must be an integer")
            proposal_text = self._required_string(raw, "proposal_text")
            cases.append(ExperimentCase(case_id, cycle_index, proposal_text))
        matrix = run_counterfactual_experiment_matrix(
            baseline=baseline,
            cases=tuple(cases),
            runner=lambda overrides: self._control_run(overrides),
        )
        return {
            "matrix": matrix.as_dict(),
            "baseline_graph_id": build_evidence_graph(baseline).id,
        }

    def _control_reproducibility(self, payload: dict[str, Any]) -> dict[str, Any]:
        baseline = self._control_run()
        raw_cases = payload.get("cases")
        if not isinstance(raw_cases, list) or not raw_cases:
            raise ValueError("cases must be a non-empty list")
        cases = []
        for raw in raw_cases:
            if not isinstance(raw, dict):
                raise ValueError("each case must be an object")
            case_id = self._required_string(raw, "id")
            cycle_index = raw.get("cycle_index")
            if isinstance(cycle_index, bool) or not isinstance(cycle_index, int):
                raise ValueError("case cycle_index must be an integer")
            cases.append(ExperimentCase(
                case_id,
                cycle_index,
                self._required_string(raw, "proposal_text"),
            ))
        matrix = run_counterfactual_experiment_matrix(
            baseline=baseline,
            cases=tuple(cases),
            runner=lambda overrides: self._control_run(overrides),
        )
        baseline_graph_id = build_evidence_graph(baseline).id
        fingerprint = fingerprint_experiment_matrix(matrix, baseline_graph_id)
        return {
            "matrix": matrix.as_dict(),
            "fingerprint": fingerprint.as_dict(),
        }

    def _control_ledger(self, payload: dict[str, Any]) -> dict[str, Any]:
        baseline = self._control_run()
        raw_cases = payload.get("cases")
        if not isinstance(raw_cases, list) or not raw_cases:
            raise ValueError("cases must be a non-empty list")
        cases = []
        for raw in raw_cases:
            if not isinstance(raw, dict):
                raise ValueError("each case must be an object")
            case_id = self._required_string(raw, "id")
            cycle_index = raw.get("cycle_index")
            if isinstance(cycle_index, bool) or not isinstance(cycle_index, int):
                raise ValueError("case cycle_index must be an integer")
            cases.append(ExperimentCase(
                case_id, cycle_index, self._required_string(raw, "proposal_text")
            ))
        matrix = run_counterfactual_experiment_matrix(
            baseline=baseline,
            cases=tuple(cases),
            runner=lambda overrides: self._control_run(overrides),
        )
        baseline_graph_id = build_evidence_graph(baseline).id
        fingerprint = fingerprint_experiment_matrix(matrix, baseline_graph_id)
        created_at = payload.get("created_at", "2026-09-30T00:00:00Z")
        record = create_experiment_ledger_record(
            matrix=matrix, fingerprint=fingerprint, created_at=created_at
        )
        with _STATE_LOCK:
            self.server.store.save_experiment_ledger(record)
        return record.as_dict()


    def _control_demo(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run one deterministic three-cycle F10.3 demonstration for Control Room."""
        run = self._control_run()
        learning = run.learning_metrics
        allocation = run.adaptive_resource_allocation(100.0, 100.0)
        return {
            "cycle_count": run.cycle_count,
            "all_converged": run.all_converged,
            "state_versions": run.state_versions,
            "cycles": [
                {
                    "index": cycle.index,
                    "proposal_id": cycle.proposal.id,
                    "proposal": cycle.proposal.proposal,
                    "parent_memory_id": cycle.parent_memory_id,
                    "parent_outcome_id": cycle.parent_outcome_id,
                    "outcome_id": cycle.result.outcome.id,
                    "utility": cycle.result.outcome.utility,
                    "omega_credit": cycle.result.credit.credit,
                    "audit": {
                        "verification_ids": list(cycle.result.consensus.verification_ids),
                        "consensus_id": cycle.result.consensus.id,
                        "convergence_id": cycle.result.convergence.id,
                        "execution_id": cycle.result.execution.id,
                        "commit_id": cycle.result.commit.id,
                        "utility_id": cycle.result.utility.id,
                        "credit_id": cycle.result.credit.id,
                        "memory_id": cycle.result.memory.id,
                        "memory_before_id": cycle.result.execution.memory_before_id,
                        "memory_after_id": cycle.result.execution.memory_after_id,
                        "compute_before_id": cycle.result.execution.compute_before_id,
                        "compute_after_id": cycle.result.execution.compute_after_id,
                        "state_id": cycle.result.state.id,
                    },
                    "metrics": {
                        "k": cycle.result.metrics.k, "c": cycle.result.metrics.c,
                        "r": cycle.result.metrics.r, "phi": cycle.result.metrics.phi,
                        "converged": cycle.result.metrics.converged,
                    },
                    "learning": {
                        "proposal_novelty": learning[cycle.index - 1].proposal_novelty,
                        "resource_efficiency": learning[cycle.index - 1].resource_efficiency,
                        "state_delta": learning[cycle.index - 1].state_delta,
                        "memory_dependency": learning[cycle.index - 1].memory_dependency,
                        "verified_improvement": learning[cycle.index - 1].verified_improvement,
                    },
                } for cycle in run.cycles
            ],
            "allocation": {
                "id": allocation.id, "improvement_bonus": allocation.improvement_bonus,
                "memory_by_cycle": allocation.memory_by_cycle, "compute_by_cycle": allocation.compute_by_cycle,
                "total_memory": allocation.total_memory, "total_compute": allocation.total_compute,
            },
            "evidence_graph": build_evidence_graph(run).as_dict(),
            "resource_state": {
                "memory_available": run.final_memory_resource.available,
                "compute_available": run.final_compute_resource.available,
                "memory_id": run.final_memory_resource.id, "compute_id": run.final_compute_resource.id,
            },
        }
    def _control_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Query the deterministic Evidence Graph produced by the Control Room demo."""
        graph = build_evidence_graph(self._control_run())
        operation = payload.get("operation", "query")
        if operation == "path":
            result = trace_evidence_path(
                graph,
                self._required_string(payload, "source_id"),
                self._required_string(payload, "target_id"),
                direction=payload.get("direction", "both"),
                max_depth=int(payload.get("max_depth", 16)),
            )
        else:
            result = query_evidence_graph(
                graph,
                self._required_string(payload, "node_id"),
                direction=payload.get("direction", "both"),
                max_depth=int(payload.get("max_depth", 1)),
                relation=payload.get("relation"),
                node_type=payload.get("node_type"),
            )
        return {"graph_id": graph.id, "query": result.as_dict()}

    def _control_replay(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run the canonical Control Room experiment twice and compare immutable artifacts."""
        original = self._control_run()
        replay = self._control_run()
        return compare_recursive_replay(original, replay).as_dict()

    def _state_snapshot(self) -> dict[str, Any]:
        with _STATE_LOCK:
            return {
                "genesis": [
                    asdict(item) | {"relations": list(item.relations)}
                    for item in self.server.store.list_genesis()
                ],
                "relations": [
                    asdict(item)
                    for item in self.server.store.list_relations()
                ],
                "closures": list(_STATE["closures"]),
                "events": list(_STATE["events"]),
            }

    @staticmethod
    def _event(kind: str, message: str) -> dict[str, str]:
        return {"kind": kind, "message": message}

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


def run_persistence_probe() -> None:
    """Verify durable Genesis -> Relation persistence when explicitly enabled."""
    if os.getenv("THENET_PERSISTENCE_PROBE") != "1":
        return

    store = create_runtime_store()
    source = create_genesis("production-persistence-source", "2026-09-30T00:00:00Z")
    target = create_genesis("production-persistence-target", "2026-09-30T00:00:00Z")
    relation = create_relation(
        source.id,
        target.id,
        "production-persistence",
        "2026-09-30T00:00:00Z",
    )

    preexisting = (
        store.get_genesis(source.id) is not None
        and store.get_genesis(target.id) is not None
        and store.get_relation(relation.id) is not None
    )
    store.save_genesis(source)
    store.save_genesis(target)
    store.save_relation(relation)
    store.close()

    reopened = create_runtime_store()
    persisted_source = reopened.get_genesis(source.id)
    persisted_target = reopened.get_genesis(target.id)
    persisted_relation = reopened.get_relation(relation.id)
    passed = (
        persisted_source == source
        and persisted_target == target
        and persisted_relation == relation
        and persisted_relation is not None
        and persisted_relation.source_id == source.id
        and persisted_relation.target_id == target.id
    )
    reopened.close()

    if not passed:
        raise RuntimeError("persistence probe failed")

    print(
        json.dumps(
            {
                "persistence_probe": "passed",
                "preexisting": preexisting,
                "genesis": [source.id, target.id],
                "relation": relation.id,
            },
            sort_keys=True,
        ),
        flush=True,
    )


def serve() -> None:
    run_persistence_probe()
    server = ThreadingHTTPServer(("0.0.0.0", runtime_port()), RuntimeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
