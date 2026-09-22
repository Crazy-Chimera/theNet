import pytest

from src.omega_credit import create_omega_credit
from src.resource_allocation import allocate_from_resource_state
from src.resource_state import create_resource_state


STAMP = "2026-09-22T00:00:00Z"


def test_allocates_only_remaining_local_capacity():
    credit_a = create_omega_credit("a", 1.0, 1.0, 1.0, True, STAMP)
    credit_b = create_omega_credit("b", 1.0, 1.0, 1.0, True, STAMP)
    resource = create_resource_state(100.0, 25.0, STAMP)

    allocations = allocate_from_resource_state([credit_a, credit_b], resource)

    assert sum(item.allocation for item in allocations) == pytest.approx(75.0)


def test_zero_remaining_capacity_produces_zero_allocations():
    credit = create_omega_credit("a", 1.0, 1.0, 1.0, True, STAMP)
    resource = create_resource_state(50.0, 60.0, STAMP)

    allocations = allocate_from_resource_state([credit], resource)

    assert allocations == (
        allocations[0],
    )
    assert allocations[0].allocation == 0.0


def test_unverified_credit_is_not_allocated():
    credit = create_omega_credit("a", 1.0, 1.0, 1.0, False, STAMP)
    resource = create_resource_state(50.0, 10.0, STAMP)

    allocations = allocate_from_resource_state([credit], resource)

    assert allocations == ()


def test_resource_input_is_immutable():
    credit = create_omega_credit("a", 1.0, 1.0, 1.0, True, STAMP)
    resource = create_resource_state(50.0, 10.0, STAMP)

    allocate_from_resource_state([credit], resource)

    assert resource.available == 50.0
    assert resource.used == 10.0


def test_wrong_resource_type_is_rejected():
    credit = create_omega_credit("a", 1.0, 1.0, 1.0, True, STAMP)

    with pytest.raises(TypeError):
        allocate_from_resource_state([credit], object())
