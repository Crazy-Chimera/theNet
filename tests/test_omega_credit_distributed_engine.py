from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.omega_credit_distributed_engine import (
    OmegaCreditEngineResult,
    run_omega_credit_engine,
)
from src.phi import create_phi
from src.relational_utility import create_relational_utility
from src.relation import create_relation
from src.resource_state import create_resource_state


STAMP = "2026-09-23T11:00:00Z"


def _inputs():
    a = create_genesis("agent-a", STAMP)
    b = create_genesis("agent-b", STAMP)
    ra = create_relation(a.id, b.id, "verified", STAMP)
    rb = create_relation(b.id, a.id, "verified", STAMP)

    utility_a = create_relational_utility(a.id, 1.0, ["e-a"], True, STAMP)
    utility_b = create_relational_utility(b.id, 0.5, ["e-b"], True, STAMP)

    structures = {
        a.id: create_phi([ra]),
        b.id: create_phi([rb]),
    }
    memory = create_resource_state(100.0, 0.0, STAMP)
    compute = create_resource_state(200.0, 0.0, STAMP)
    return (utility_a, utility_b), structures, memory, compute


def test_engine_composes_full_distributed_path():
    utilities, structures, memory, compute = _inputs()

    result = run_omega_credit_engine(
        utilities, structures, memory, compute, STAMP
    )

    assert isinstance(result, OmegaCreditEngineResult)
    assert len(result.credits) == 2
    assert len(result.ledger.entries) == 2
    assert result.distribution.total_credit > 0.0
    assert sum(share for _, _, share in result.distribution.contributions) == pytest.approx(1.0)
    assert result.memory_resource.used > memory.used
    assert result.compute_resource.used > compute.used


def test_input_order_does_not_change_ledger_distribution_or_allocation():
    utilities, structures, memory, compute = _inputs()

    left = run_omega_credit_engine(
        utilities, structures, memory, compute, STAMP
    )
    right = run_omega_credit_engine(
        tuple(reversed(utilities)), structures, memory, compute, STAMP
    )

    assert left.ledger == right.ledger
    assert left.distribution == right.distribution
    assert left.allocation == right.allocation


def test_unverified_contribution_receives_zero_credit():
    utilities, structures, memory, compute = _inputs()
    unverified = create_relational_utility(
        utilities[0].contributor_id, 1.0, ["e-a"], False, STAMP
    )

    result = run_omega_credit_engine(
        (unverified, utilities[1]), structures, memory, compute, STAMP
    )

    assert result.credits[0].credit == 0.0


def test_missing_structure_is_rejected():
    utilities, structures, memory, compute = _inputs()
    del structures[utilities[0].contributor_id]

    with pytest.raises(ValueError, match="missing Φ structure"):
        run_omega_credit_engine(
            utilities, structures, memory, compute, STAMP
        )


def test_duplicate_contributor_is_rejected():
    utilities, structures, memory, compute = _inputs()

    with pytest.raises(ValueError, match="each contributor"):
        run_omega_credit_engine(
            (utilities[0], utilities[0]), structures, memory, compute, STAMP
        )


def test_result_is_immutable():
    utilities, structures, memory, compute = _inputs()
    result = run_omega_credit_engine(
        utilities, structures, memory, compute, STAMP
    )

    with pytest.raises(FrozenInstanceError):
        result.memory_resource = memory
