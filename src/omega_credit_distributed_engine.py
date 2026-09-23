"""Deterministic multi-contributor Ω-Credit engine for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence

from src.contribution_ledger import ContributionLedger, create_contribution_ledger
from src.omega_credit import OmegaCredit, create_omega_credit_from_utility
from src.omega_credit_allocation import (
    OmegaCreditAllocation,
    create_omega_credit_allocation,
)
from src.omega_credit_engine import (
    OmegaCreditDistribution,
    create_omega_credit_distribution_from_ledger,
)
from src.omega_credit_resource_commitment import apply_omega_credit_allocation
from src.phi_coherence import phi_coherence
from src.relational_utility import RelationalUtility
from src.resource_state import ResourceState
from src.structure import PhiStructure


@dataclass(frozen=True)
class OmegaCreditEngineResult:
    credits: tuple[OmegaCredit, ...]
    ledger: ContributionLedger
    distribution: OmegaCreditDistribution
    allocation: OmegaCreditAllocation
    memory_resource: ResourceState
    compute_resource: ResourceState


def run_omega_credit_engine(
    utilities: Sequence[RelationalUtility],
    structures_by_contributor: Mapping[str, PhiStructure],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    created_at: str,
) -> OmegaCreditEngineResult:
    """Compose Φ coherence, Ω-Credit accounting, allocation and commit."""
    if not isinstance(memory_resource, ResourceState):
        raise TypeError("memory_resource must be ResourceState")
    if not isinstance(compute_resource, ResourceState):
        raise TypeError("compute_resource must be ResourceState")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    records = tuple(utilities)
    if any(not isinstance(item, RelationalUtility) for item in records):
        raise TypeError("utilities must contain RelationalUtility values")

    if len({item.contributor_id for item in records}) != len(records):
        raise ValueError("each contributor may appear only once")

    memory_efficiency = 1.0 - memory_resource.efficiency
    compute_efficiency = 1.0 - compute_resource.efficiency
    combined_efficiency = (memory_efficiency + compute_efficiency) / 2.0

    credits = tuple(
        create_omega_credit_from_utility(
            utility,
            resource_efficiency=combined_efficiency,
            coherence=_require_coherence(
                structures_by_contributor,
                utility.contributor_id,
            ),
            created_at=created_at,
        )
        for utility in records
    )

    ledger = create_contribution_ledger(credits)
    distribution = create_omega_credit_distribution_from_ledger(ledger)
    allocation = create_omega_credit_allocation(
        distribution,
        memory_resource.available - memory_resource.used,
        compute_resource.available - compute_resource.used,
    )
    memory_after, compute_after = apply_omega_credit_allocation(
        allocation,
        memory_resource,
        compute_resource,
        created_at,
    )

    return OmegaCreditEngineResult(
        credits=credits,
        ledger=ledger,
        distribution=distribution,
        allocation=allocation,
        memory_resource=memory_after,
        compute_resource=compute_after,
    )


def _require_coherence(
    structures_by_contributor: Mapping[str, PhiStructure],
    contributor_id: str,
) -> float:
    structure = structures_by_contributor.get(contributor_id)
    if not isinstance(structure, PhiStructure):
        raise ValueError(f"missing Φ structure for contributor {contributor_id}")
    return phi_coherence(structure)


__all__ = ["OmegaCreditEngineResult", "run_omega_credit_engine"]
