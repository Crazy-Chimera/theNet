from dataclasses import replace

from src.counterfactual_experiment_matrix import ExperimentCase, run_counterfactual_experiment_matrix
from src.counterfactual_reproducibility import fingerprint_experiment_matrix
from src.evidence_graph import build_evidence_graph
from src.experiment_ledger import create_experiment_ledger_record
from src.experiment_memory_bridge import bridge_verified_experiment_to_memory
from tests.test_counterfactual_replay import _runner


def _ledger(proposal):
    build = _runner()
    baseline = build()
    matrix = run_counterfactual_experiment_matrix(
        baseline=baseline,
        cases=(ExperimentCase("a", 2, proposal),),
        runner=build,
    )
    fingerprint = fingerprint_experiment_matrix(matrix, build_evidence_graph(baseline).id)
    return create_experiment_ledger_record(
        matrix=matrix, fingerprint=fingerprint,
        created_at="2026-09-30T12:00:00Z",
    )


def test_independent_reproduction_bridges_to_memory():
    first = _ledger("same")
    second = _ledger("same")
    bridge = bridge_verified_experiment_to_memory(
        baseline=first, verification=second,
        subject_id="agent-subject", created_at="2026-09-30T12:01:00Z",
    )
    assert bridge.verified is True
    assert bridge.memory is not None
    assert bridge.memory.source_id == first.id
    assert bridge.memory.kind == "verified-experiment"


def test_changed_experiment_cannot_enter_memory():
    first = _ledger("same")
    second = _ledger("changed")
    bridge = bridge_verified_experiment_to_memory(
        baseline=first, verification=second,
        subject_id="agent-subject", created_at="2026-09-30T12:01:00Z",
    )
    assert bridge.verified is False
    assert bridge.memory is None


def test_same_record_cannot_self_verify():
    first = _ledger("same")
    bridge = bridge_verified_experiment_to_memory(
        baseline=first, verification=first,
        subject_id="agent-subject", created_at="2026-09-30T12:01:00Z",
    )
    assert bridge.verified is False
    assert bridge.memory is None


def test_tampered_ledger_identity_is_rejected():
    first = _ledger("same")
    tampered = replace(
        first,
        fingerprint=replace(first.fingerprint, result_fingerprint="tampered"),
    )
    try:
        bridge_verified_experiment_to_memory(
            baseline=tampered, verification=first,
            subject_id="agent-subject", created_at="2026-09-30T12:01:00Z",
        )
    except ValueError as exc:
        assert "fingerprint" in str(exc)
    else:
        raise AssertionError("tampered ledger must be rejected")
