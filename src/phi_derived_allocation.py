"""Φ-derived coherence adapter for self-organizing allocation."""

from __future__ import annotations

from typing import Mapping

from src.phi_coherence import phi_coherence
from src.relational_utility import RelationalUtility
from src.resource_state import ResourceState
from src.self_organizing_allocation import (
    SelfOrganizingAllocation,
    allocate_memory_and_compute,
)
from src.structure import PhiStructure


def allocate_memory_and_compute_from_phi(
    utilities: list[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    structures_by_contributor: Mapping[str, PhiStructure],
) -> SelfOrganizingAllocation:
    """Derive contributor coherence from Φ before allocating Ω-Credit."""
    utility_records = tuple(utilities)
    coherence_by_contributor: dict[str, float] = {}

    for utility in utility_records:
        if not isinstance(utility, RelationalUtility):
            raise TypeError("utilities must contain RelationalUtility values")

        structure = structures_by_contributor.get(utility.contributor_id)
        if not isinstance(structure, PhiStructure):
            raise ValueError(
                f"missing Φ structure for contributor {utility.contributor_id}"
            )

        coherence_by_contributor[utility.contributor_id] = phi_coherence(structure)

    return allocate_memory_and_compute(
        utility_records,
        memory_resource,
        compute_resource,
        coherence_by_contributor,
    )
