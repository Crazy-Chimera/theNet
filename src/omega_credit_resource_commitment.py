"""Immutable ResourceState transition from an Ω-Credit allocation."""

from __future__ import annotations

import math

from src.omega_credit_allocation import OmegaCreditAllocation
from src.resource_state import ResourceState, create_resource_state


def _allocation_total(values: tuple[tuple[str, float], ...]) -> float:
    total = math.fsum(value for _contributor_id, value in values)
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("allocation totals must be finite and non-negative")
    return total


def _apply(
    resource: ResourceState,
    allocated: float,
    created_at: str,
) -> ResourceState:
    remaining = max(resource.available - resource.used, 0.0)
    tolerance = max(1e-12, abs(remaining) * 1e-12)
    if allocated > remaining + tolerance:
        raise ValueError("allocation exceeds remaining resource capacity")
    if allocated == 0.0:
        return resource
    return create_resource_state(
        available=resource.available,
        used=resource.used + allocated,
        created_at=created_at,
    )


def apply_omega_credit_allocation(
    allocation: OmegaCreditAllocation,
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Apply allocation totals as immutable memory/compute state transitions."""
    if not isinstance(allocation, OmegaCreditAllocation):
        raise TypeError("allocation must be an OmegaCreditAllocation")
    if not isinstance(memory_resource, ResourceState):
        raise TypeError("memory_resource must be a ResourceState")
    if not isinstance(compute_resource, ResourceState):
        raise TypeError("compute_resource must be a ResourceState")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    memory_allocated = _allocation_total(allocation.memory_by_contributor)
    compute_allocated = _allocation_total(allocation.compute_by_contributor)

    return (
        _apply(memory_resource, memory_allocated, created_at),
        _apply(compute_resource, compute_allocated, created_at),
    )


__all__ = ["apply_omega_credit_allocation"]
