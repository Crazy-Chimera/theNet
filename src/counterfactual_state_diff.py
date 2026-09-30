"""Content-level state diff for isolated counterfactual Agent Ω runs.

This module compares observable runtime fields, not only content-derived IDs.
It remains descriptive: differences are runtime state changes, not a claim of
causal effect outside the modeled computation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.counterfactual_replay import CounterfactualComparison
from src.recursive_convergence import RecursiveConvergenceRun


@dataclass(frozen=True)
class FieldDiff:
    cycle_index: int
    scope: str
    field: str
    baseline: Any
    counterfactual: Any
    delta: float | None
    changed: bool
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CounterfactualStateDiff:
    selected_cycle: int
    first_divergence_cycle: int | None
    first_divergence_artifact: str | None
    fields: tuple[FieldDiff, ...]
    changed_field_count: int
    propagation_cycles: tuple[int, ...]
    version: int = 1

    def as_dict(self) -> dict:
        return {
            "selected_cycle": self.selected_cycle,
            "first_divergence_cycle": self.first_divergence_cycle,
            "first_divergence_artifact": self.first_divergence_artifact,
            "fields": [item.as_dict() for item in self.fields],
            "changed_field_count": self.changed_field_count,
            "propagation_cycles": list(self.propagation_cycles),
            "version": self.version,
        }


def _delta(left: Any, right: Any) -> float | None:
    if isinstance(left, bool) or isinstance(right, bool):
        return None
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return float(right) - float(left)
    return None


def _append_scope(
    output: list[FieldDiff],
    cycle_index: int,
    scope: str,
    left: dict[str, Any],
    right: dict[str, Any],
    fields: tuple[str, ...],
) -> None:
    for field in fields:
        baseline = left[field]
        counterfactual = right[field]
        changed = baseline != counterfactual
        output.append(
            FieldDiff(
                cycle_index=cycle_index,
                scope=scope,
                field=field,
                baseline=baseline,
                counterfactual=counterfactual,
                delta=_delta(baseline, counterfactual),
                changed=changed,
            )
        )


def build_counterfactual_state_diff(
    comparison: CounterfactualComparison,
    baseline: RecursiveConvergenceRun,
    counterfactual: RecursiveConvergenceRun,
) -> CounterfactualStateDiff:
    """Compare observable state, metrics, utility, credit and resources."""
    if baseline.cycle_count != counterfactual.cycle_count:
        raise ValueError("baseline and counterfactual must have equal cycle counts")

    fields: list[FieldDiff] = []
    propagation: list[int] = []

    for index in range(1, baseline.cycle_count + 1):
        left_cycle = baseline.cycles[index - 1]
        right_cycle = counterfactual.cycles[index - 1]
        left_result = left_cycle.result
        right_result = right_cycle.result

        state_left = asdict(left_result.state)
        state_right = asdict(right_result.state)
        metric_left = asdict(left_result.metrics)
        metric_right = asdict(right_result.metrics)
        utility_left = asdict(left_result.utility)
        utility_right = asdict(right_result.utility)
        credit_left = asdict(left_result.credit)
        credit_right = asdict(right_result.credit)
        memory_left = asdict(left_result.memory_resource)
        memory_right = asdict(right_result.memory_resource)
        compute_left = asdict(left_result.compute_resource)
        compute_right = asdict(right_result.compute_resource)
        outcome_left = asdict(left_result.outcome)
        outcome_right = asdict(right_result.outcome)

        _append_scope(fields, index, "state", state_left, state_right,
                      ("subject_id", "singularity_id", "created_at", "version"))
        _append_scope(fields, index, "metrics", metric_left, metric_right,
                      ("k", "c", "r", "phi", "converged"))
        _append_scope(fields, index, "outcome", outcome_left, outcome_right,
                      ("result", "success", "utility"))
        _append_scope(fields, index, "utility", utility_left, utility_right,
                      ("value", "verified"))
        _append_scope(fields, index, "omega_credit", credit_left, credit_right,
                      ("relational_utility", "resource_efficiency", "coherence", "verified", "credit"))
        _append_scope(fields, index, "memory_resource", memory_left, memory_right,
                      ("available", "used", "efficiency"))
        _append_scope(fields, index, "compute_resource", compute_left, compute_right,
                      ("available", "used", "efficiency"))

        if any(item.changed for item in fields if item.cycle_index == index):
            propagation.append(index)

    changed = tuple(item for item in fields if item.changed)
    return CounterfactualStateDiff(
        selected_cycle=comparison.cycle_index,
        first_divergence_cycle=comparison.replay.first_divergence_cycle,
        first_divergence_artifact=comparison.replay.first_divergence_artifact,
        fields=tuple(fields),
        changed_field_count=len(changed),
        propagation_cycles=tuple(propagation),
    )


__all__ = ["CounterfactualStateDiff", "FieldDiff", "build_counterfactual_state_diff"]
