from __future__ import annotations

import pytest

from src.omega_credit import create_omega_credit
from src.omega_credit_engine import create_omega_credit_distribution
from src.omega_credit_runtime import (
    OmegaCreditAllocation,
    allocate_omega_credit_resources,
)


STAMP = "2026-09-22T14:00:00Z"


def test_runtime_facade_delegates_canonical_allocation():
    distribution = create_omega_credit_distribution(
        [
            create_omega_credit("agent:a", 2.0, "evidence:a", STAMP),
            create_omega_credit("agent:b", 1.0, "evidence:b", STAMP),
        ]
    )

    allocation = allocate_omega_credit_resources(distribution, 30.0, 60.0)

    assert isinstance(allocation, OmegaCreditAllocation)
    assert allocation.memory_by_contributor == (
        ("agent:a", pytest.approx(20.0)),
        ("agent:b", pytest.approx(10.0)),
    )
    assert allocation.compute_by_contributor == (
        ("agent:a", pytest.approx(40.0)),
        ("agent:b", pytest.approx(20.0)),
    )


def test_runtime_facade_is_deterministic():
    distribution = create_omega_credit_distribution(
        [create_omega_credit("agent:a", 1.0, "evidence:a", STAMP)]
    )

    first = allocate_omega_credit_resources(distribution, 10.0, 20.0)
    second = allocate_omega_credit_resources(distribution, 10.0, 20.0)

    assert first == second
    assert first.id == second.id


def test_runtime_facade_preserves_validation_boundary():
    distribution = create_omega_credit_distribution(
        [create_omega_credit("agent:a", 1.0, "evidence:a", STAMP)]
    )

    with pytest.raises(ValueError):
        allocate_omega_credit_resources(distribution, -1.0, 20.0)
