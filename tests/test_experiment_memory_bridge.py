from dataclasses import replace

from src.counterfactual_experiment_matrix import ExperimentCase, run_counterfactual_experiment_matrix
from src.counterfactual_reproducibility import fingerprint_experiment_matrix
from src.evidence_graph import build_evidence_graph
from src.experiment_ledger import create_experiment_ledger_record
from src.experiment_memory_bridge import bridge_verified_experiment_to_memory
from tests.test_counterfactual_replay import _runner


def _ledger():
    build = _runner()
    baseline = build()
    matrix = run_counterfactual_experiment_matrix(
        baseline=baseline,
        cases=(ExperimentCase("a", 2, "A"),),
        runner=build,
    )
    fingerprint = fingerprint_experiment_matrix(matrix, build_evidence_graph(baseline).id)
    return create_experiment_ledger_record(
        matrix=matrix,
        fingerprint=fingerprint,
        created_at="2026-09-30T12:00:00Z",
    )


def test_verified_ledger_bridges_to_memory():
    ledger = _ledger()
    bridge = bridge_verified_experiment_to_memory(
        ledger=ledger,
        subject_id="agent-subject",
        verification_id="verification-123",
        created_at="2026-09-30T12:00:01Z",
    )
    assert bridge.ledger_id == ledger.id
    assert bridge.memory.source_id == ledger.id
    assert bridge.memory.kind == "verified-experiment"
    assert bridge.verification_id == "verification-123"


def test_invalid_ledger_identity_cannot_bridge():
    ledger = _ledger()
    tampered = replace(
        ledger,
        fingerprint=replace(ledger.fingerprint, result_fingerprint="tampered"),
    )
    try:
        bridge_verified_experiment_to_memory(
            ledger=tampered,
            subject_id="agent-subject",
            verification_id="verification-123",
            created_at="2026-09-30T12:00:01Z",
        )
    except ValueError as exc:
        assert "fingerprint" in str(exc)
    else:
        raise AssertionError("tampered ledger must be rejected")
