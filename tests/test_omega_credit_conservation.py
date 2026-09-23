from dataclasses import FrozenInstanceError, replace

import pytest

from src.omega_credit_conservation import (
    OmegaCreditConservationAudit,
    audit_omega_credit_conservation,
)
from src.omega_credit_distributed_engine import run_omega_credit_engine
from src.genesis import create_genesis
from src.phi import create_phi
from src.relation import create_relation
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state
from src.omega_credit_engine import OmegaCreditDistribution


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


def test_valid_result_is_conserved():
    result = _result()
    audit = audit_omega_credit_conservation(
        result, 0.0, 0.0, 100.0, 200.0
    )

    assert audit == OmegaCreditConservationAudit(True)


def test_audit_is_deterministic_and_immutable():
    result = _result()
    first = audit_omega_credit_conservation(result, 0.0, 0.0, 100.0, 200.0)
    second = audit_omega_credit_conservation(result, 0.0, 0.0, 100.0, 200.0)

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.valid = False


def test_ledger_mismatch_is_rejected():
    result = _result()
    ledger = replace(result.ledger, totals=((result.credits[0].contributor_id, 999.0),))
    invalid = replace(result, ledger=ledger)

    audit = audit_omega_credit_conservation(
        invalid, 0.0, 0.0, 100.0, 200.0
    )

    assert not audit.valid
    assert audit.reason == "ledger total mismatch"


def test_distribution_mismatch_is_rejected():
    result = _result()
    distribution = replace(
        result.distribution,
        total_credit=result.distribution.total_credit + 1.0,
    )
    invalid = replace(result, distribution=distribution)

    audit = audit_omega_credit_conservation(
        invalid, 0.0, 0.0, 100.0, 200.0
    )

    assert not audit.valid
    assert audit.reason == "distribution total mismatch"


def test_negative_allocation_is_rejected():
    result = _result()
    allocation = replace(
        result.allocation,
        memory_by_contributor=(
            (result.allocation.memory_by_contributor[0][0], -1.0),
        ),
    )
    invalid = replace(result, allocation=allocation)

    audit = audit_omega_credit_conservation(
        invalid, 0.0, 0.0, 100.0, 200.0
    )

    assert not audit.valid
    assert audit.reason == "negative allocation"


def test_capacity_overflow_is_rejected():
    result = _result()
    audit = audit_omega_credit_conservation(
        result, 0.0, 0.0, 0.0, 0.0
    )

    assert not audit.valid
    assert audit.reason == "memory allocation exceeds capacity"


def test_resource_commit_mismatch_is_rejected():
    result = _result()
    audit = audit_omega_credit_conservation(
        result, 1.0, 0.0, 100.0, 200.0
    )

    assert not audit.valid
    assert audit.reason == "memory commit mismatch"


def test_zero_credit_cannot_increase_resources():
    result = _result()
    zero_distribution = replace(
        result.distribution,
        total_credit=0.0,
        contributions=tuple(
            (contributor_id, 0.0, 0.0)
            for contributor_id, _credit, _share
            in result.distribution.contributions
        ),
    )
    zero_allocation = replace(
        result.allocation,
        memory_by_contributor=tuple(
            (contributor_id, 0.0)
            for contributor_id, _value in result.allocation.memory_by_contributor
        ),
        compute_by_contributor=tuple(
            (contributor_id, 0.0)
            for contributor_id, _value in result.allocation.compute_by_contributor
        ),
    )
    memory = create_resource_state(100.0, 1.0, STAMP)
    compute = create_resource_state(200.0, 1.0, STAMP)
    invalid = replace(
        result,
        distribution=zero_distribution,
        allocation=zero_allocation,
        memory_resource=memory,
        compute_resource=compute,
    )

    audit = audit_omega_credit_conservation(
        invalid, 0.0, 0.0, 100.0, 200.0
    )

    assert not audit.valid
    assert audit.reason == "memory commit mismatch"


def test_wrong_result_type_is_rejected():
    with pytest.raises(TypeError):
        audit_omega_credit_conservation(object(), 0.0, 0.0, 1.0, 1.0)
