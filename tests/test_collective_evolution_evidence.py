from dataclasses import FrozenInstanceError

import pytest

from src.collective_evolution_evidence import (
    CollectiveEvolutionEvidence,
    create_collective_evolution_evidence,
)
from src.omega_credit_evolution_receipt_binding import (
    OmegaCreditEvolutionReceiptBinding,
)


STAMP = "2026-09-23T00:00:00Z"


def binding(
    commit_id: str,
    receipt_id: str,
    result_id: str,
    created_at: str = STAMP,
) -> OmegaCreditEvolutionReceiptBinding:
    return OmegaCreditEvolutionReceiptBinding(
        id=f"binding-{commit_id}-{receipt_id}",
        commit_id=commit_id,
        receipt_id=receipt_id,
        result_id=result_id,
        created_at=created_at,
    )


def test_collective_evidence_aggregates_bindings():
    first = binding("commit-a", "receipt-a", "result-a")
    second = binding("commit-b", "receipt-b", "result-b")

    evidence = create_collective_evolution_evidence([first, second], STAMP)

    assert isinstance(evidence, CollectiveEvolutionEvidence)
    assert evidence.binding_ids == tuple(sorted((first.id, second.id)))
    assert evidence.commit_ids == ("commit-a", "commit-b")
    assert evidence.receipt_ids == ("receipt-a", "receipt-b")
    assert evidence.result_ids == ("result-a", "result-b")
    assert evidence.created_at == STAMP


def test_collective_evidence_is_order_independent():
    first = binding("commit-a", "receipt-a", "result-a")
    second = binding("commit-b", "receipt-b", "result-b")

    assert create_collective_evolution_evidence([first, second], STAMP) == (
        create_collective_evolution_evidence([second, first], STAMP)
    )


def test_collective_evidence_deduplicates_binding_ids():
    first = binding("commit-a", "receipt-a", "result-a")

    evidence = create_collective_evolution_evidence([first, first], STAMP)

    assert evidence.binding_ids == (first.id,)
    assert evidence.commit_ids == ("commit-a",)


def test_empty_collective_evidence_is_valid():
    evidence = create_collective_evolution_evidence([], STAMP)

    assert evidence.binding_ids == ()
    assert evidence.commit_ids == ()
    assert evidence.receipt_ids == ()
    assert evidence.result_ids == ()


def test_changed_binding_set_changes_identity():
    first = binding("commit-a", "receipt-a", "result-a")
    second = binding("commit-b", "receipt-b", "result-b")

    assert create_collective_evolution_evidence([first], STAMP).id != (
        create_collective_evolution_evidence([first, second], STAMP).id
    )


def test_changed_timestamp_changes_identity():
    first = binding("commit-a", "receipt-a", "result-a")

    assert create_collective_evolution_evidence([first], STAMP).id != (
        create_collective_evolution_evidence([first], "2026-09-23T00:00:01Z").id
    )


def test_invalid_binding_is_rejected():
    with pytest.raises(TypeError):
        create_collective_evolution_evidence([object()], STAMP)


def test_empty_timestamp_is_rejected():
    with pytest.raises(ValueError):
        create_collective_evolution_evidence([], "")


def test_evidence_is_immutable():
    evidence = create_collective_evolution_evidence([], STAMP)

    with pytest.raises(FrozenInstanceError):
        evidence.version = 2
