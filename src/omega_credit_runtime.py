"""Agent Ω Ω-Credit resource allocation facade."""

from __future__ import annotations

from src.omega_credit_allocation import (
    OmegaCreditAllocation,
    create_omega_credit_allocation,
)
from src.omega_credit_engine import OmegaCreditDistribution


def allocate_omega_credit_resources(
    distribution: OmegaCreditDistribution,
    memory_capacity: float,
    compute_capacity: float,
) -> OmegaCreditAllocation:
    """Expose canonical Ω-Credit allocation without duplicating allocation logic."""
    return create_omega_credit_allocation(
        distribution,
        memory_capacity,
        compute_capacity,
    )


__all__ = ["OmegaCreditAllocation", "allocate_omega_credit_resources"]
