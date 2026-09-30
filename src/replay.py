"""Deterministic and forensic replay primitives for Agent Ω recursive runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.evidence_graph import build_evidence_graph
from src.recursive_convergence import RecursiveConvergenceRun


ARTIFACT_TYPES = (
    "proposal",
    "consensus",
    "convergence",
    "execution",
    "commit",
    "outcome",
    "utility",
    "omega_credit",
    "memory",
    "state",
)


@dataclass(frozen=True)
class ReplayArtifactComparison:
    cycle_index: int
    artifact_type: str
    original_id: str
    replay_id: str
    match: bool
    version: int = 1


@dataclass(frozen=True)
class ReplayComparison:
    original_graph_id: str
    replay_graph_id: str
    graph_match: bool
    run_match: bool
    artifact_match: bool
    original_cycles: int
    replay_cycles: int
    artifact_comparisons: tuple[ReplayArtifactComparison, ...] = ()
    first_divergence_cycle: int | None = None
    first_divergence_artifact: str | None = None
    first_divergence_original_id: str | None = None
    first_divergence_replay_id: str | None = None
    version: int = 2

    @property
    def deterministic(self) -> bool:
        return self.graph_match and self.run_match and self.artifact_match

    def as_dict(self) -> dict:
        return asdict(self) | {"deterministic": self.deterministic}


def _artifact_ids(run: RecursiveConvergenceRun) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (
            cycle.proposal.id,
            cycle.result.consensus.id,
            cycle.result.convergence.id,
            cycle.result.execution.id,
            cycle.result.commit.id,
            cycle.result.outcome.id,
            cycle.result.utility.id,
            cycle.result.credit.id,
            cycle.result.memory.id,
            cycle.result.state.id,
        )
        for cycle in run.cycles
    )


def _build_artifact_comparisons(
    original: RecursiveConvergenceRun,
    replay: RecursiveConvergenceRun,
) -> tuple[ReplayArtifactComparison, ...]:
    comparisons: list[ReplayArtifactComparison] = []
    original_ids = _artifact_ids(original)
    replay_ids = _artifact_ids(replay)
    cycle_count = max(len(original_ids), len(replay_ids))

    for cycle_offset in range(cycle_count):
        left = original_ids[cycle_offset] if cycle_offset < len(original_ids) else ()
        right = replay_ids[cycle_offset] if cycle_offset < len(replay_ids) else ()
        for artifact_offset, artifact_type in enumerate(ARTIFACT_TYPES):
            original_id = left[artifact_offset] if artifact_offset < len(left) else "<missing>"
            replay_id = right[artifact_offset] if artifact_offset < len(right) else "<missing>"
            comparisons.append(
                ReplayArtifactComparison(
                    cycle_index=cycle_offset + 1,
                    artifact_type=artifact_type,
                    original_id=original_id,
                    replay_id=replay_id,
                    match=original_id == replay_id,
                )
            )
    return tuple(comparisons)


def compare_recursive_replay(
    original: RecursiveConvergenceRun,
    replay: RecursiveConvergenceRun,
) -> ReplayComparison:
    """Compare two immutable recursive runs and locate the first divergence."""
    if not isinstance(original, RecursiveConvergenceRun):
        raise TypeError("original must be RecursiveConvergenceRun")
    if not isinstance(replay, RecursiveConvergenceRun):
        raise TypeError("replay must be RecursiveConvergenceRun")

    original_graph = build_evidence_graph(original)
    replay_graph = build_evidence_graph(replay)
    artifact_comparisons = _build_artifact_comparisons(original, replay)
    first = next((item for item in artifact_comparisons if not item.match), None)

    return ReplayComparison(
        original_graph_id=original_graph.id,
        replay_graph_id=replay_graph.id,
        graph_match=original_graph == replay_graph,
        run_match=original == replay,
        artifact_match=all(item.match for item in artifact_comparisons),
        original_cycles=original.cycle_count,
        replay_cycles=replay.cycle_count,
        artifact_comparisons=artifact_comparisons,
        first_divergence_cycle=first.cycle_index if first else None,
        first_divergence_artifact=first.artifact_type if first else None,
        first_divergence_original_id=first.original_id if first else None,
        first_divergence_replay_id=first.replay_id if first else None,
    )


__all__ = [
    "ARTIFACT_TYPES",
    "ReplayArtifactComparison",
    "ReplayComparison",
    "compare_recursive_replay",
]
