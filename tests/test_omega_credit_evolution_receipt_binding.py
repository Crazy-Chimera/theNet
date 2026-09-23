from dataclasses import FrozenInstanceError

import pytest

from src.commit import EvolutionCommit
from src.omega_credit_evolution_receipt_binding import (
    OmegaCreditEvolutionReceiptBinding,
    create_omega_credit_evolution_receipt_binding,
)
from src.omega_credit_verified_receipt import OmegaCreditVerifiedReceipt


STAMP = "2026-09-23T12:00:00Z"


def make_commit() -> EvolutionCommit:
    return EvolutionCommit(
        id="commit-1",
        previous_state_id="state-1",
        proposal_id="proposal-1",
        verification_ids=("verification-1",),
        convergence_id="convergence-1",
        created_at=STAMP,
    )


def make_receipt(audit_valid: bool = True) -> OmegaCreditVerifiedReceipt:
    return OmegaCreditVerifiedReceipt(
        id="receipt-1",
        result_id="result-1",
        audit_valid=audit_valid,
        memory_before_used=0.0,
        compute_before_used=0.0,
        memory_capacity=100.0,
        compute_capacity=200.0,
    )


def test_valid_binding_is_created():
    binding = create_omega_credit_evolution_receipt_binding(
        make_commit(), make_receipt(), STAMP
    )

    assert isinstance(binding, OmegaCreditEvolutionReceiptBinding)
    assert binding.commit_id == "commit-1"
    assert binding.receipt_id == "receipt-1"
    assert binding.result_id == "result-1"


def test_binding_is_deterministic():
    first = create_omega_credit_evolution_receipt_binding(
        make_commit(), make_receipt(), STAMP
    )
    second = create_omega_credit_evolution_receipt_binding(
        make_commit(), make_receipt(), STAMP
    )

    assert first == second


def test_binding_changes_when_any_reference_changes():
    commit = make_commit()
    receipt = make_receipt()
    first = create_omega_credit_evolution_receipt_binding(commit, receipt, STAMP)
    changed_receipt = OmegaCreditVerifiedReceipt(
        id="receipt-2",
        result_id="result-2",
        audit_valid=True,
        memory_before_used=0.0,
        compute_before_used=0.0,
        memory_capacity=100.0,
        compute_capacity=200.0,
    )
    second = create_omega_credit_evolution_receipt_binding(
        commit, changed_receipt, STAMP
    )

    assert first.id != second.id


def test_binding_is_immutable():
    binding = create_omega_credit_evolution_receipt_binding(
        make_commit(), make_receipt(), STAMP
    )

    with pytest.raises(FrozenInstanceError):
        binding.version = 2


def test_invalid_receipt_is_rejected():
    with pytest.raises(ValueError, match="audit-valid"):
        create_omega_credit_evolution_receipt_binding(
            make_commit(), make_receipt(False), STAMP
        )


@pytest.mark.parametrize(
    "commit, receipt, created_at, error",
    [
        (object(), make_receipt(), STAMP, "EvolutionCommit"),
        (make_commit(), object(), STAMP, "OmegaCreditVerifiedReceipt"),
        (make_commit(), make_receipt(), "", "created_at"),
    ],
)
def test_invalid_inputs_are_rejected(commit, receipt, created_at, error):
    with pytest.raises((TypeError, ValueError), match=error):
        create_omega_credit_evolution_receipt_binding(
            commit, receipt, created_at
        )


def test_binding_does_not_mutate_sources():
    commit = make_commit()
    receipt = make_receipt()

    create_omega_credit_evolution_receipt_binding(commit, receipt, STAMP)

    assert commit.id == "commit-1"
    assert receipt.id == "receipt-1"
