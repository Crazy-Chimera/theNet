from dataclasses import replace

from src.collective_evolution_evidence import create_collective_evolution_evidence
from src.collective_evolution_evidence_verification import (
    verify_collective_evolution_evidence,
)
from src.omega_credit_evolution_receipt_binding import (
    OmegaCreditEvolutionReceiptBinding,
)


STAMP = "2026-09-23T00:00:00Z"


def binding(
    binding_id: str,
    commit_id: str,
    receipt_id: str,
    result_id: str,
) -> OmegaCreditEvolutionReceiptBinding:
    return OmegaCreditEvolutionReceiptBinding(
        id=binding_id,
        commit_id=commit_id,
        receipt_id=receipt_id,
        result_id=result_id,
        created_at=STAMP,
    )


def test_verification_accepts_exact_reference_surface():
    first = binding("binding-a", "commit-a", "receipt-a", "result-a")
    second = binding("binding-b", "commit-b", "receipt-b", "result-b")

    evidence = create_collective_evolution_evidence([first, second], STAMP)

    assert verify_collective_evolution_evidence(evidence, [first, second]) is True


def test_verification_is_order_independent_for_supplied_bindings():
    first = binding("binding-a", "commit-a", "receipt-a", "result-a")
    second = binding("binding-b", "commit-b", "receipt-b", "result-b")

    evidence = create_collective_evolution_evidence([first, second], STAMP)

    assert verify_collective_evolution_evidence(evidence, [second, first]) is True


def test_empty_evidence_requires_empty_binding_set():
    evidence = create_collective_evolution_evidence([], STAMP)

    assert verify_collective_evolution_evidence(evidence, []) is True
    assert verify_collective_evolution_evidence(
        evidence,
        [binding("binding-a", "commit-a", "receipt-a", "result-a")],
    ) is False


def test_missing_binding_is_rejected():
    first = binding("binding-a", "commit-a", "receipt-a", "result-a")
    second = binding("binding-b", "commit-b", "receipt-b", "result-b")

    evidence = create_collective_evolution_evidence([first, second], STAMP)

    assert verify_collective_evolution_evidence(evidence, [first]) is False


def test_extra_binding_is_rejected():
    first = binding("binding-a", "commit-a", "receipt-a", "result-a")
    second = binding("binding-b", "commit-b", "receipt-b", "result-b")
    extra = binding("binding-c", "commit-c", "receipt-c", "result-c")

    evidence = create_collective_evolution_evidence([first, second], STAMP)

    assert verify_collective_evolution_evidence(evidence, [first, second, extra]) is False


def test_mismatched_binding_payload_is_rejected():
    first = binding("binding-a", "commit-a", "receipt-a", "result-a")
    second = binding("binding-b", "commit-b", "receipt-b", "result-b")
    tampered = replace(first, commit_id="commit-tampered")

    evidence = create_collective_evolution_evidence([first, second], STAMP)

    assert verify_collective_evolution_evidence(evidence, [tampered, second]) is False


def test_duplicate_supplied_binding_is_rejected():
    first = binding("binding-a", "commit-a", "receipt-a", "result-a")

    evidence = create_collective_evolution_evidence([first], STAMP)

    assert verify_collective_evolution_evidence(evidence, [first, first]) is False


def test_non_binding_input_is_rejected():
    evidence = create_collective_evolution_evidence([], STAMP)

    assert verify_collective_evolution_evidence(evidence, [object()]) is False
