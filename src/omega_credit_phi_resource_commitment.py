"""End-to-end Ω-Credit commitment using Φ-derived coherence."""

from __future__ import annotations

from typing import Mapping

from src.omega_credit_self_organizing_commitment import (
    commit_self_organizing_allocation,
)
from src.phi_derived_allocation import derive_phi_coherence
from src.relational_utility import RelationalUtility
from src.resource_state import ResourceState
from src.structure import PhiStructure


def commit_self_organizing_allocation_from_phi(
    utilities: list[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    structures_by_contributor: Mapping[str, PhiStructure],
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Derive Φ coherence and commit the resulting local allocation."""
    utility_records = tuple(utilities)
    coherence_by_contributor = derive_phi_coherence(
        utility_records,
        structures_by_contributor,
    )

    return commit_self_organizing_allocation(
        utility_records,
        memory_resource,
        compute_resource,
        coherence_by_contributor,
        created_at,
    )


__all__ = ["commit_self_organizing_allocation_from_phi"]
