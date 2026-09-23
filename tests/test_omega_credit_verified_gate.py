from dataclasses import replace

import pytest

import src.omega_credit_verified_gate as gate
from src.genesis import create_genesis
from src.omega_credit_verified_gate import run_verified_omega_credit_engine
from src.phi import create_phi
from src.relation import create_relation
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state
from src.omega_credit_distributed_engine import OmegaCreditEngineResult


STAMP = "2026-09-23T12:00:00Z"


def _inputs():
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
    return utilities, structures, memory, compute


def test_verified_gate_returns_engine_result():
    utilities, structures, memory, compute = _inputs()

    result = run_verified_omega_credit_engine(
        utilities,
        structures,
        memory,
        compute,
        STAMP,
        0.0,
        0.0,
        100.0,
        200.0,
    )

    assert isinstance(result, OmegaCreditEngineResult)
    assert result.distribution.total_credit > 0.0


def test_verified_gate_preserves_immutable_result():
    utilities, structures, memory, compute = _inputs()

    first = run_verified_omega_credit_engine(
        utilities,
        structures,
        memory,
        compute,
        STAMP,
        0.0,
        0.0,
        100.0,
        200.0,
    )
    second = run_verified_omega_credit_engine(
        utilities,
        structures,
        memory,
        compute,
        STAMP,
        0.0,
        0.0,
        100.0,
        200.0,
    )

    assert first == second


def test_failed_audit_blocks_execution_boundary(monkeypatch):
    utilities, structures, memory, compute = _inputs()

    class FailedAudit:
        valid = False
        reason = "forced failure"

    monkeypatch.setattr(gate, "audit_omega_credit_conservation", lambda *args: FailedAudit())

    with pytest.raises(ValueError, match="forced failure"):
        run_verified_omega_credit_engine(
            utilities,
            structures,
            memory,
            compute,
            STAMP,
            0.0,
            0.0,
            100.0,
            200.0,
        )


def test_gate_rejects_invalid_resource_input_through_engine():
    utilities, structures, _memory, compute = _inputs()
    invalid_memory = replace(
        compute,
        available=-1.0,
    )

    with pytest.raises(ValueError):
        run_verified_omega_credit_engine(
            utilities,
            structures,
            invalid_memory,
            compute,
            STAMP,
            0.0,
            0.0,
            100.0,
            200.0,
        )


def test_gate_rejects_insufficient_capacity():
    utilities, structures, memory, compute = _inputs()

    with pytest.raises(ValueError, match="memory allocation exceeds capacity"):
        run_verified_omega_credit_engine(
            utilities,
            structures,
            memory,
            compute,
            STAMP,
            0.0,
            0.0,
            0.0,
            200.0,
        )
