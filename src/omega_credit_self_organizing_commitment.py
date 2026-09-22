"""End-to-end immutable Ω-Credit self-organizing commitment facade."""

from __future__ import annotations

from hashlib import sha256
import json

from src.contribution_ledger import ContributionLedger
from src.omega_credit_allocation import (
    OmegaCreditAllocation,
    create_omega_credit_allocation,
)
from src.omega_credit_engine import (
    create_omega_credit_distribution_from_ledger,
)
from src.omega_credit_resource_commitment import apply_omega_credit_allocation
from src.resource_state import ResourceState
from src.relational_utility import RelationalUtility
from src.self_organizing_allocation import allocate_memory_and_compute


def _allocation_id(
    memory_by_contributor: tuple[tuple[str, float], ...],
    compute_by_contributor: tuple[tuple[str, float], ...],
) -> str:
    canonical = json.dumps(
        {
            "compute_by_contributor": compute_by_contributor,
            "memory_by_contributor": memory_by_contributor,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def commit_self_organizing_allocation(
    utilities: tuple[RelationalUtility, ...],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    coherence_by_contributor: dict[str, float],
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Derive and apply local memory/compute allocation without side effects."""
    allocation = allocate_memory_and_compute(
        utilities=utilities,
        memory_resource=memory_resource,
        compute_resource=compute_resource,
        coherence_by_contributor=coherence_by_contributor,
    )

    memory_by_contributor = tuple(
        (item.contributor_id, item.allocation) for item in allocation.memory
    )
    compute_by_contributor = tuple(
        (item.contributor_id, item.allocation) for item in allocation.compute
    )

    resource_allocation = OmegaCreditAllocation(
        id=_allocation_id(memory_by_contributor, compute_by_contributor),
        memory_by_contributor=memory_by_contributor,
        compute_by_contributor=compute_by_contributor,
    )

    return apply_omega_credit_allocation(
        resource_allocation,
        memory_resource,
        compute_resource,
        created_at,
    )


def commit_ledger_backed_allocation(
    ledger: ContributionLedger,
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    memory_capacity: float,
    compute_capacity: float,
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Commit resource use from one canonical persistent contribution history."""
    if not isinstance(ledger, ContributionLedger):
        raise TypeError("ledger must be a ContributionLedger")

    distribution = create_omega_credit_distribution_from_ledger(ledger)
    allocation = create_omega_credit_allocation(
        distribution,
        memory_capacity,
        compute_capacity,
    )

    return apply_omega_credit_allocation(
        allocation,
        memory_resource,
        compute_resource,
        created_at,
    )


__all__ = [
    "commit_ledger_backed_allocation",
    "commit_self_organizing_allocation",
]
