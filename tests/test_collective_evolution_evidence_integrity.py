from dataclasses import replace

from src.collective_evolution_evidence import CollectiveEvolutionEvidence
from src.collective_evolution_evidence_integrity import (
    verify_collective_evolution_evidence_integrity,
)


STAMP = "2026-09-23T12:00:00Z"


def _evidence():
    return CollectiveEvolutionEvidence(
        id="evidence-a",
        binding_ids=("binding-a", "binding-b"),
        commit_ids=("commit-a", "commit-b"),
        receipt_ids=("receipt-a", "receipt-b"),
        result_ids=("result-a", "result-b"),
        created_at=STAMP,
    )


def test_integrity_accepts_valid_evidence():
    assert verify_collective_evolution_evidence_integrity(_evidence()) is True


def test_integrity_is_deterministic():
    evidence = _evidence()
    assert verify_collective_evolution_evidence_integrity(evidence) is True
    assert verify_collective_evolution_evidence_integrity(evidence) is True


def test_integrity_accepts_empty_reference_surface():
    evidence = CollectiveEvolutionEvidence(
        id="evidence-empty",
        binding_ids=(),
        commit_ids=(),
        receipt_ids=(),
        result_ids=(),
        created_at=STAMP,
    )
    assert verify_collective_evolution_evidence_integrity(evidence) is True


def test_integrity_rejects_duplicate_binding_ids():
    evidence = replace(_evidence(), binding_ids=("binding-a", "binding-a"))
    assert verify_collective_evolution_evidence_integrity(evidence) is False


def test_integrity_rejects_cardinality_mismatch():
    evidence = replace(_evidence(), result_ids=("result-a",))
    assert verify_collective_evolution_evidence_integrity(evidence) is False


def test_integrity_rejects_empty_identifier():
    evidence = replace(_evidence(), commit_ids=("commit-a", ""))
    assert verify_collective_evolution_evidence_integrity(evidence) is False


def test_integrity_rejects_empty_timestamp():
    evidence = replace(_evidence(), created_at="")
    assert verify_collective_evolution_evidence_integrity(evidence) is False


def test_integrity_rejects_unsupported_version():
    evidence = replace(_evidence(), version=2)
    assert verify_collective_evolution_evidence_integrity(evidence) is False


def test_integrity_rejects_non_evidence_input():
    assert verify_collective_evolution_evidence_integrity(object()) is False
