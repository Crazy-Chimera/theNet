"""Observable impact vector for counterfactual Agent Ω branches.

The vector is a structured difference, not a preference, score, or causal claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from src.counterfactual_replay import CounterfactualComparison
from src.counterfactual_state_diff import CounterfactualStateDiff
from src.recursive_convergence import RecursiveConvergenceRun


@dataclass(frozen=True)
class ImpactVector:
    cycle_index: int
    delta_k: float
    delta_c: float
    delta_r: int
    delta_phi: float
    delta_utility: float
    delta_omega_credit: float
    delta_memory_available: float
    delta_compute_available: float
    delta_state_version: int
    changed_fields: int
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CounterfactualImpactVector:
    selected_cycle: int
    first_divergence_cycle: int | None
    first_divergence_artifact: str | None
    vectors: tuple[ImpactVector, ...]
    aggregate: ImpactVector
    version: int = 1

    def as_dict(self) -> dict:
        return {
            "selected_cycle": self.selected_cycle,
            "first_divergence_cycle": self.first_divergence_cycle,
            "first_divergence_artifact": self.first_divergence_artifact,
            "vectors": [v.as_dict() for v in self.vectors],
            "aggregate": self.aggregate.as_dict(),
            "version": self.version,
        }


def _field_delta(diff: CounterfactualStateDiff, cycle: int, scope: str, field: str) -> float:
    for item in diff.fields:
        if item.cycle_index == cycle and item.scope == scope and item.field == field:
            return float(item.delta or 0.0)
    return 0.0


def _changed_count(diff: CounterfactualStateDiff, cycle: int) -> int:
    return sum(item.changed for item in diff.fields if item.cycle_index == cycle)


def build_counterfactual_impact_vector(
    comparison: CounterfactualComparison,
    baseline: RecursiveConvergenceRun,
    counterfactual: RecursiveConvergenceRun,
    state_diff: CounterfactualStateDiff,
) -> CounterfactualImpactVector:
    if baseline.cycle_count != counterfactual.cycle_count:
        raise ValueError("baseline and counterfactual must have equal cycle counts")
    if state_diff.selected_cycle != comparison.cycle_index:
        raise ValueError("state diff and comparison must select the same cycle")

    vectors = []
    for index in range(1, baseline.cycle_count + 1):
        left = baseline.cycles[index - 1].result
        right = counterfactual.cycles[index - 1].result
        vectors.append(ImpactVector(
            cycle_index=index,
            delta_k=right.metrics.k - left.metrics.k,
            delta_c=right.metrics.c - left.metrics.c,
            delta_r=right.metrics.r - left.metrics.r,
            delta_phi=right.metrics.phi - left.metrics.phi,
            delta_utility=right.outcome.utility - left.outcome.utility,
            delta_omega_credit=right.credit.credit - left.credit.credit,
            delta_memory_available=right.memory_resource.available - left.memory_resource.available,
            delta_compute_available=right.compute_resource.available - left.compute_resource.available,
            delta_state_version=right.state.version - left.state.version,
            changed_fields=_changed_count(state_diff, index),
        ))

    aggregate = ImpactVector(
        cycle_index=0,
        delta_k=sum(v.delta_k for v in vectors),
        delta_c=sum(v.delta_c for v in vectors),
        delta_r=sum(v.delta_r for v in vectors),
        delta_phi=sum(v.delta_phi for v in vectors),
        delta_utility=sum(v.delta_utility for v in vectors),
        delta_omega_credit=sum(v.delta_omega_credit for v in vectors),
        delta_memory_available=sum(v.delta_memory_available for v in vectors),
        delta_compute_available=sum(v.delta_compute_available for v in vectors),
        delta_state_version=sum(v.delta_state_version for v in vectors),
        changed_fields=sum(v.changed_fields for v in vectors),
    )
    return CounterfactualImpactVector(
        selected_cycle=comparison.cycle_index,
        first_divergence_cycle=comparison.replay.first_divergence_cycle,
        first_divergence_artifact=comparison.replay.first_divergence_artifact,
        vectors=tuple(vectors),
        aggregate=aggregate,
    )


__all__ = ["ImpactVector", "CounterfactualImpactVector", "build_counterfactual_impact_vector"]
