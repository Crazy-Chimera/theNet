"""Verified execution boundary for the distributed Ω-Credit engine."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from src.omega_credit_conservation import audit_omega_credit_conservation
from src.omega_credit_distributed_engine import (
    OmegaCreditEngineResult,
    run_omega_credit_engine,
)
from src.relational_utility import RelationalUtility
from src.resource_state import ResourceState
from src.structure import PhiStructure


def run_verified_omega_credit_engine(
    utilities: Sequence[RelationalUtility],
    structures_by_contributor: Mapping[str, PhiStructure],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    created_at: str,
    memory_before_used: float,
    compute_before_used: float,
    memory_capacity: float,
    compute_capacity: float,
) -> OmegaCreditEngineResult:
    """Run the Ω-Credit engine and require a passing conservation audit."""
    result = run_omega_credit_engine(
        utilities,
        structures_by_contributor,
        memory_resource,
        compute_resource,
        created_at,
    )
    audit = audit_omega_credit_conservation(
        result,
        memory_before_used,
        compute_before_used,
        memory_capacity,
        compute_capacity,
    )
    if not audit.valid:
        raise ValueError(f"Ω-Credit conservation audit failed: {audit.reason}")

    return result


__all__ = ["run_verified_omega_credit_engine"]
