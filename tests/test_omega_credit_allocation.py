from dataclasses import FrozenInstanceError

import pytest

from src.omega_credit import create_omega_credit
from src.omega_credit_allocation import (
    OmegaCreditAllocation,
    create_omega_credit_allocation,
)
from src.omega_credit_engine import create_omega_credit_distribution


STAMP = "2026-09-22T12:00:00Z"


def credit(contributor: str, value: float):
    return create_omega_credit(
        contributor_id=contributor,
        relational_utility=value,
        resource_efficiency=1.0,
        coherence=1.0,
        verified=True,
        created_at=STAMP,
    )


def distribution():
    return create_omega_credit_distribution(
        [credit("b", 0.25), credit("a", 0.75)]
    )


def test_allocation_is_proportional():
    state = create_omega_credit_allocation(
        distribution(),
        memory_capacity=100.0,
        compute_capacity=40.0,
    )

    assert isinstance(state, OmegaCreditAllocation)
    assert state.memory_by_contributor == (
        ("a", pytest.approx(75.0)),
        ("b", pytest.approx(25.0)),
    )
    assert state.compute_by_contributor == (
        ("a", pytest.approx(30.0)),
        ("b", pytest.approx(10.0)),
    )


def test_allocations_sum_to_capacity():
    state = create_omega_credit_allocation(
        distribution(),
        memory_capacity=100.0,
        compute_capacity=40.0,
    )

    assert sum(value for _, value in state.memory_by_contributor) == pytest.approx(100.0)
    assert sum(value for _, value in state.compute_by_contributor) == pytest.approx(40.0)


def test_zero_credit_produces_zero_allocations():
    zero = create_omega_credit_distribution(
        [
            create_omega_credit("a", 0.0, 1.0, 1.0, False, STAMP),
            create_omega_credit("b", 0.0, 1.0, 1.0, False, STAMP),
        ]
    )

    state = create_omega_credit_allocation(zero, 100.0, 40.0)

    assert state.memory_by_contributor == (("a", 0.0), ("b", 0.0))
    assert state.compute_by_contributor == (("a", 0.0), ("b", 0.0))


def test_empty_distribution_is_valid():
    zero = create_omega_credit_distribution([])

    state = create_omega_credit_allocation(zero, 100.0, 40.0)

    assert state.memory_by_contributor == ()
    assert state.compute_by_contributor == ()


def test_input_order_cannot_change_allocation():
    first = create_omega_credit_distribution([credit("a", 0.2), credit("b", 0.8)])
    second = create_omega_credit_distribution([credit("b", 0.8), credit("a", 0.2)])

    assert create_omega_credit_allocation(first, 10.0, 20.0) == (
        create_omega_credit_allocation(second, 10.0, 20.0)
    )


@pytest.mark.parametrize("value", [-1.0, float("inf"), float("nan")])
def test_memory_capacity_must_be_finite_and_non_negative(value):
    with pytest.raises(ValueError):
        create_omega_credit_allocation(distribution(), value, 1.0)


@pytest.mark.parametrize("value", [-1.0, float("inf"), float("nan")])
def test_compute_capacity_must_be_finite_and_non_negative(value):
    with pytest.raises(ValueError):
        create_omega_credit_allocation(distribution(), 1.0, value)


def test_boolean_capacity_is_rejected():
    with pytest.raises(ValueError):
        create_omega_credit_allocation(distribution(), True, 1.0)


def test_wrong_distribution_type_is_rejected():
    with pytest.raises(TypeError):
        create_omega_credit_allocation(object(), 1.0, 1.0)


def test_allocation_is_immutable():
    state = create_omega_credit_allocation(distribution(), 1.0, 1.0)

    with pytest.raises(FrozenInstanceError):
        state.version = 2


def test_allocation_identity_is_deterministic():
    first = create_omega_credit_allocation(distribution(), 100.0, 40.0)
    second = create_omega_credit_allocation(distribution(), 100.0, 40.0)

    assert first.id == second.id
