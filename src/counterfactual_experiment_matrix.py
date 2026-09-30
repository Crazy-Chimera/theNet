"""Deterministic matrix of isolated counterfactual experiments.

Each hypothesis is compared independently against the same immutable baseline.
The matrix contains descriptive impact vectors; it does not rank hypotheses.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.counterfactual_impact_vector import (
    CounterfactualImpactVector,
    build_counterfactual_impact_vector,
)
from src.counterfactual_replay import CounterfactualSpec, run_counterfactual
from src.counterfactual_state_diff import build_counterfactual_state_diff
from src.recursive_convergence import RecursiveConvergenceRun


@dataclass(frozen=True)
class ExperimentCase:
    id: str
    cycle_index: int
    proposal_text: str
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentResult:
    case: ExperimentCase
    impact_vector: CounterfactualImpactVector
    version: int = 1

    def as_dict(self) -> dict:
        return {
            "case": self.case.as_dict(),
            "impact_vector": self.impact_vector.as_dict(),
            "version": self.version,
        }


@dataclass(frozen=True)
class CounterfactualExperimentMatrix:
    baseline_cycles: int
    cases: tuple[ExperimentResult, ...]
    version: int = 1

    @property
    def case_count(self) -> int:
        return len(self.cases)

    def as_dict(self) -> dict:
        return {
            "baseline_cycles": self.baseline_cycles,
            "case_count": self.case_count,
            "cases": [case.as_dict() for case in self.cases],
            "version": self.version,
        }


def run_counterfactual_experiment_matrix(
    *,
    baseline: RecursiveConvergenceRun,
    cases: tuple[ExperimentCase, ...],
    runner,
) -> CounterfactualExperimentMatrix:
    if not isinstance(baseline, RecursiveConvergenceRun):
        raise TypeError("baseline must be RecursiveConvergenceRun")
    if not isinstance(cases, tuple) or not cases:
        raise ValueError("cases must be a non-empty tuple")
    if not callable(runner):
        raise TypeError("runner must be callable")

    ids: set[str] = set()
    results: list[ExperimentResult] = []
    for case in cases:
        if not isinstance(case, ExperimentCase):
            raise TypeError("cases must contain ExperimentCase values")
        if case.id in ids:
            raise ValueError("case ids must be unique")
        ids.add(case.id)
        spec = CounterfactualSpec(case.cycle_index, case.proposal_text)
        branch, comparison = run_counterfactual(
            baseline=baseline,
            spec=spec,
            runner=runner,
        )
        diff = build_counterfactual_state_diff(comparison, baseline, branch)
        impact = build_counterfactual_impact_vector(
            comparison, baseline, branch, diff
        )
        results.append(ExperimentResult(case=case, impact_vector=impact))

    return CounterfactualExperimentMatrix(
        baseline_cycles=baseline.cycle_count,
        cases=tuple(results),
    )


__all__ = [
    "CounterfactualExperimentMatrix",
    "ExperimentCase",
    "ExperimentResult",
    "run_counterfactual_experiment_matrix",
]
