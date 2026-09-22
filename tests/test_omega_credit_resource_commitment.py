from dataclasses import FrozenInstanceError

import pytest

from src.omega_credit_allocation import create_omega_credit_allocation
from src.omega_credit_engine import OmegaCreditDistribution
from src.omega_credit_resource_commitment import apply_omega_credit_allocation
from src.resource_state import create_resource_state


def _allocation():
    distribution = OmegaCreditDistribution(
        id="distribution",
        total_credit=4.0,
        contributions=(
            ("a", 1.0, 0.25),
            ("b", 3.0, 0.75),
        ),
    )
    return create_omega_credit_allocation(distribution, 80.0, 40.0)


def test_applies_allocation_to_each_resource_independently():
    allocation = _allocation()
    memory = create_resource_state(100.0, 10.0, "t0")
    compute = create_resource_state(50.0, 5.0, "t0")

    next_memory, next_compute = apply_omega_credit_allocation(
        allocation, memory, compute, "t1"
    )

    assert next_memory.available == 100.0
    assert next_memory.used == 90.0
    assert next_compute.available == 50.0
    assert next_compute.used == 45.0


def test_zero_allocation_preserves_resource_identity():
    allocation = create_omega_credit_allocation(
        OmegaCreditDistribution(
            id="zero",
            total_credit=0.0,
            contributions=(),
        ),
        80.0,
        40.0,
    )
    memory = create_resource_state(100.0, 10.0, "t0")
    compute = create_resource_state(50.0, 5.0, "t0")

    next_memory, next_compute = apply_omega_credit_allocation(
        allocation, memory, compute, "t1"
    )

    assert next_memory is memory
    assert next_compute is compute


def test_inputs_are_not_mutated():
    allocation = _allocation()
    memory = create_resource_state(100.0, 10.0, "t0")
    compute = create_resource_state(50.0, 5.0, "t0")

    apply_omega_credit_allocation(allocation, memory, compute, "t1")

    assert memory.used == 10.0
    assert compute.used == 5.0


def test_rejects_over_allocation():
    allocation = _allocation()
    memory = create_resource_state(50.0, 10.0, "t0")
    compute = create_resource_state(50.0, 5.0, "t0")

    with pytest.raises(ValueError, match="remaining resource capacity"):
        apply_omega_credit_allocation(allocation, memory, compute, "t1")


def test_output_is_immutable():
    allocation = _allocation()
    memory = create_resource_state(100.0, 10.0, "t0")
    compute = create_resource_state(50.0, 5.0, "t0")

    next_memory, _ = apply_omega_credit_allocation(
        allocation, memory, compute, "t1"
    )

    with pytest.raises(FrozenInstanceError):
        next_memory.used = 0.0
