"""Counterfactual replay primitives for Agent Ω.

A counterfactual run never mutates the baseline RecursiveConvergenceRun.
It supplies an explicit input override to a deterministic runner and then
uses the forensic replay comparison to expose the first downstream divergence.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass

from src.recursive_convergence import RecursiveConvergenceRun
from src.replay import ReplayComparison, compare_recursive_replay


@dataclass(frozen=True)
class CounterfactualSpec:
    cycle_index: int
    proposal_text: str
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CounterfactualComparison:
    baseline_graph_id: str
    counterfactual_graph_id: str
    baseline_cycles: int
    counterfactual_cycles: int
    cycle_index: int
    baseline_proposal: str
    counterfactual_proposal: str
    replay: ReplayComparison
    version: int = 1

    @property
    def deterministic_baseline(self) -> bool:
        return self.replay.original_cycles == self.replay.replay_cycles

    @property
    def diverged(self) -> bool:
        return not self.replay.artifact_match

    def as_dict(self) -> dict:
        return {
            "baseline_graph_id": self.baseline_graph_id,
            "counterfactual_graph_id": self.counterfactual_graph_id,
            "baseline_cycles": self.baseline_cycles,
            "counterfactual_cycles": self.counterfactual_cycles,
            "cycle_index": self.cycle_index,
            "baseline_proposal": self.baseline_proposal,
            "counterfactual_proposal": self.counterfactual_proposal,
            "diverged": self.diverged,
            "deterministic_baseline": self.deterministic_baseline,
            "replay": self.replay.as_dict(),
            "version": self.version,
        }


CounterfactualRunner = Callable[[dict[int, str]], RecursiveConvergenceRun]


def validate_counterfactual_spec(
    baseline: RecursiveConvergenceRun,
    spec: CounterfactualSpec,
) -> None:
    if not isinstance(baseline, RecursiveConvergenceRun):
        raise TypeError("baseline must be RecursiveConvergenceRun")
    if not isinstance(spec, CounterfactualSpec):
        raise TypeError("spec must be CounterfactualSpec")
    if spec.cycle_index < 1 or spec.cycle_index > baseline.cycle_count:
        raise ValueError("cycle_index must reference an existing baseline cycle")
    if not isinstance(spec.proposal_text, str) or not spec.proposal_text.strip():
        raise ValueError("proposal_text must be non-empty")


def run_counterfactual(
    *,
    baseline: RecursiveConvergenceRun,
    spec: CounterfactualSpec,
    runner: CounterfactualRunner,
) -> tuple[RecursiveConvergenceRun, CounterfactualComparison]:
    """Run one isolated counterfactual and compare it with the immutable baseline."""
    validate_counterfactual_spec(baseline, spec)
    if not callable(runner):
        raise TypeError("runner must be callable")

    counterfactual = runner({spec.cycle_index: spec.proposal_text})
    comparison = compare_counterfactual(baseline, counterfactual, spec)
    return counterfactual, comparison


def compare_counterfactual(
    baseline: RecursiveConvergenceRun,
    counterfactual: RecursiveConvergenceRun,
    spec: CounterfactualSpec,
) -> CounterfactualComparison:
    """Compare a counterfactual run without mutating either run."""
    validate_counterfactual_spec(baseline, spec)
    if not isinstance(counterfactual, RecursiveConvergenceRun):
        raise TypeError("counterfactual must be RecursiveConvergenceRun")
    if counterfactual.cycle_count != baseline.cycle_count:
        raise ValueError("counterfactual must preserve baseline cycle count")

    replay = compare_recursive_replay(baseline, counterfactual)
    baseline_proposal = baseline.cycles[spec.cycle_index - 1].proposal.proposal
    counterfactual_proposal = counterfactual.cycles[spec.cycle_index - 1].proposal.proposal

    return CounterfactualComparison(
        baseline_graph_id=replay.original_graph_id,
        counterfactual_graph_id=replay.replay_graph_id,
        baseline_cycles=baseline.cycle_count,
        counterfactual_cycles=counterfactual.cycle_count,
        cycle_index=spec.cycle_index,
        baseline_proposal=baseline_proposal,
        counterfactual_proposal=counterfactual_proposal,
        replay=replay,
    )


__all__ = [
    "CounterfactualComparison",
    "CounterfactualRunner",
    "CounterfactualSpec",
    "compare_counterfactual",
    "run_counterfactual",
    "validate_counterfactual_spec",
]
