"""Self-organizing memory and compute allocation for theNet."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

from src.omega_allocation import CreditAllocation, allocate_credit
from src.omega_credit import create_omega_credit_from_utility
from src.relational_utility import RelationalUtility
from src.resource_state import ResourceState


@dataclass(frozen=True)
class SelfOrganizingAllocation:
    memory: tuple[CreditAllocation, ...]
    compute: tuple[CreditAllocation, ...]
    version: int = 1


def _validate_coherence(coherence: float) -> float:
    if isinstance(coherence, bool) or not isinstance(coherence, (int, float)):
        raise ValueError("coherence must be a finite number in [0, 1]")
    normalized = float(coherence)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("coherence must be a finite number in [0, 1]")
    return normalized


def _remaining(resource: ResourceState) -> float:
    return max(resource.available - resource.used, 0.0)


def _credits(
    utilities: Iterable[RelationalUtility],
    resource_efficiency: float,
    coherence_by_contributor: Mapping[str, float],
):
    result = []
    for utility in utilities:
        if not isinstance(utility, RelationalUtility):
            raise TypeError("utilities must contain RelationalUtility values")
        if utility.contributor_id not in coherence_by_contributor:
            raise ValueError(
                f"missing Φ coherence for contributor {utility.contributor_id}"
            )
        coherence = _validate_coherence(
            coherence_by_contributor[utility.contributor_id]
        )
        result.append(
            create_omega_credit_from_utility(
                utility,
                resource_efficiency=resource_efficiency,
                coherence=coherence,
                created_at=utility.created_at,
            )
        )
    return result


def allocate_memory_and_compute(
    utilities: Iterable[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    coherence_by_contributor: Mapping[str, float],
) -> SelfOrganizingAllocation:
    if not isinstance(memory_resource, ResourceState):
        raise TypeError("memory_resource must be ResourceState")
    if not isinstance(compute_resource, ResourceState):
        raise TypeError("compute_resource must be ResourceState")

    utility_records = tuple(utilities)
    memory_credits = _credits(
        utility_records,
        memory_resource.efficiency,
        coherence_by_contributor,
    )
    compute_credits = _credits(
        utility_records,
        compute_resource.efficiency,
        coherence_by_contributor,
    )

    return SelfOrganizingAllocation(
        memory=allocate_credit(memory_credits, _remaining(memory_resource)),
        compute=allocate_credit(compute_credits, _remaining(compute_resource)),
    )
