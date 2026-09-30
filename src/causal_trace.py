"""Forensic dependency trace for counterfactual Agent Ω branches.

The trace describes modeled artifact dependencies. It does not claim physical
causality; it exposes the dependency structure encoded by the runtime.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.counterfactual_replay import CounterfactualComparison
from src.recursive_convergence import RecursiveConvergenceRun
from src.replay import ARTIFACT_TYPES


@dataclass(frozen=True)
class CausalTraceStep:
    cycle_index: int
    source_type: str
    source_original_id: str
    source_counterfactual_id: str
    relation: str
    target_type: str
    target_original_id: str
    target_counterfactual_id: str
    changed: bool
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CausalTrace:
    selected_cycle: int
    first_divergence_cycle: int | None
    first_divergence_artifact: str | None
    steps: tuple[CausalTraceStep, ...]
    propagation_cycles: tuple[int, ...]
    changed_artifacts: tuple[str, ...]
    version: int = 1

    @property
    def modeled_dependency_chain(self) -> tuple[str, ...]:
        return tuple(
            f"C{step.cycle_index}:{step.source_type}"
            f"-[{step.relation}]->C{step.cycle_index}:{step.target_type}"
            for step in self.steps
        )

    def as_dict(self) -> dict:
        return {
            "selected_cycle": self.selected_cycle,
            "first_divergence_cycle": self.first_divergence_cycle,
            "first_divergence_artifact": self.first_divergence_artifact,
            "steps": [step.as_dict() for step in self.steps],
            "propagation_cycles": list(self.propagation_cycles),
            "changed_artifacts": list(self.changed_artifacts),
            "modeled_dependency_chain": list(self.modeled_dependency_chain),
            "version": self.version,
        }


_RELATIONS = (
    ("proposal", "consensus", "verified_by_consensus"),
    ("consensus", "convergence", "converges"),
    ("convergence", "execution", "authorizes_execution"),
    ("execution", "commit", "commits"),
    ("commit", "outcome", "produces"),
    ("outcome", "utility", "measured_as"),
    ("utility", "omega_credit", "credits"),
    ("outcome", "memory", "remembered_as"),
    ("memory", "state", "influences"),
)


def _artifact_id_map(run: RecursiveConvergenceRun, cycle_index: int) -> dict[str, str]:
    result = run.cycles[cycle_index - 1].result
    proposal = run.cycles[cycle_index - 1].proposal
    return {
        "proposal": proposal.id,
        "consensus": result.consensus.id,
        "convergence": result.convergence.id,
        "execution": result.execution.id,
        "commit": result.commit.id,
        "outcome": result.outcome.id,
        "utility": result.utility.id,
        "omega_credit": result.credit.id,
        "memory": result.memory.id,
        "state": result.state.id,
    }


def build_causal_trace(
    comparison: CounterfactualComparison,
    baseline: RecursiveConvergenceRun,
    counterfactual: RecursiveConvergenceRun,
) -> CausalTrace:
    """Build a deterministic dependency trace from the selected branch onward."""
    if baseline.cycle_count != counterfactual.cycle_count:
        raise ValueError("baseline and counterfactual must have equal cycle counts")

    first_cycle = comparison.replay.first_divergence_cycle
    first_artifact = comparison.replay.first_divergence_artifact
    if first_cycle is None:
        return CausalTrace(
            selected_cycle=comparison.cycle_index,
            first_divergence_cycle=None,
            first_divergence_artifact=None,
            steps=(),
            propagation_cycles=(),
            changed_artifacts=(),
        )

    steps: list[CausalTraceStep] = []
    changed_artifacts: list[str] = []
    propagation_cycles: list[int] = []

    for cycle_index in range(first_cycle, baseline.cycle_count + 1):
        left = _artifact_id_map(baseline, cycle_index)
        right = _artifact_id_map(counterfactual, cycle_index)
        cycle_changed = any(left[k] != right[k] for k in ARTIFACT_TYPES)
        if cycle_changed:
            propagation_cycles.append(cycle_index)
        for source_type, target_type, relation in _RELATIONS:
            changed = (
                left[source_type] != right[source_type]
                or left[target_type] != right[target_type]
            )
            if changed:
                changed_artifacts.extend(
                    [f"C{cycle_index}:{source_type}", f"C{cycle_index}:{target_type}"]
                )
            steps.append(
                CausalTraceStep(
                    cycle_index=cycle_index,
                    source_type=source_type,
                    source_original_id=left[source_type],
                    source_counterfactual_id=right[source_type],
                    relation=relation,
                    target_type=target_type,
                    target_original_id=left[target_type],
                    target_counterfactual_id=right[target_type],
                    changed=changed,
                )
            )

        if cycle_index < baseline.cycle_count:
            next_left = _artifact_id_map(baseline, cycle_index + 1)
            next_right = _artifact_id_map(counterfactual, cycle_index + 1)
            changed = left["memory"] != right["memory"] or next_left["proposal"] != next_right["proposal"]
            steps.append(
                CausalTraceStep(
                    cycle_index=cycle_index,
                    source_type="memory",
                    source_original_id=left["memory"],
                    source_counterfactual_id=right["memory"],
                    relation="informs_next_proposal",
                    target_type="proposal",
                    target_original_id=next_left["proposal"],
                    target_counterfactual_id=next_right["proposal"],
                    changed=changed,
                )
            )

    return CausalTrace(
        selected_cycle=comparison.cycle_index,
        first_divergence_cycle=first_cycle,
        first_divergence_artifact=first_artifact,
        steps=tuple(steps),
        propagation_cycles=tuple(propagation_cycles),
        changed_artifacts=tuple(dict.fromkeys(changed_artifacts)),
    )


__all__ = ["CausalTrace", "CausalTraceStep", "build_causal_trace"]
