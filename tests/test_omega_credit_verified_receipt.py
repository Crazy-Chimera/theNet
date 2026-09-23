from dataclasses import FrozenInstanceError, replace

import pytest

from src.genesis import create_genesis
from src.omega_credit_distributed_engine import run_omega_credit_engine
from src.omega_credit_verified_receipt import (
    OmegaCreditVerifiedReceipt,
    create_omega_credit_verified_receipt,
)
from src.phi import create_phi
from src.relation import create_relation
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state


STAMP = "2026-09-23T12:00:00Z"


def _result():
    a = create_genesis("agent-a", STAMP)
    b = create_genesis("agent-b", STAMP)
    ra = create_relation(a.id, b.id, "verified", STAMP)
    rb = create_relation(b.id, a.id, "verified", STAMP)
    utilities = (
        create_relational_utility(a.id, 1.0, ["e-a"], True, STAMP),
        create_relational_utility(b.id, 0.5, ["e-b"], True, STAMP),
    )
    structures = {a.id: create_phi([ra]), b.id: create_phi([rb])}
    memory = create_resource_state(100.0, 0.0, STAMP)
    compute = create_resource_state(200.0, 0.0, STAMP)
    return run_omega_credit_engine(
        utilities, structures, memory, compute, STAMP
    )


def _receipt():
    return create_omega_credit_verified_receipt(
        _result(), 0.0, 0.0, 100.0, 200.0
    )


def test_valid_result_creates_verified_receipt():
    receipt = _receipt()

    assert isinstance(receipt, OmegaCreditVerifiedReceipt)
    assert receipt.audit_valid is True
    assert receipt.result_id
    assert receipt.id


def test_receipt_is_deterministic():
    assert _receipt() == _receipt()


def test_receipt_is_immutable():
    receipt = _receipt()

    with pytest.raises(FrozenInstanceError):
        receipt.audit_valid = False


def test_receipt_changes_when_audit_inputs_change():
    result = _result()
    first = create_omega_credit_verified_receipt(
        result, 0.0, 0.0, 100.0, 200.0
    )
    second = create_omega_credit_verified_receipt(
        result, 0.0, 0.0, 101.0, 200.0
    )

    assert first.result_id == second.result_id
    assert first.id != second.id


def test_invalid_result_cannot_create_receipt():
    result = _result()
    invalid = replace(
        result,
        distribution=replace(
            result.distribution,
            total_credit=result.distribution.total_credit + 1.0,
        ),
    )

    with pytest.raises(ValueError, match="distribution total mismatch"):
        create_omega_credit_verified_receipt(
            invalid, 0.0, 0.0, 100.0, 200.0
        )


def test_receipt_creation_does_not_mutate_result():
    result = _result()
    before = result

    create_omega_credit_verified_receipt(
        result, 0.0, 0.0, 100.0, 200.0
    )

    assert result == before
