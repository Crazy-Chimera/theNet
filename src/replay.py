"""Deterministic replay primitives for Agent Ω recursive runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.evidence_graph import build_evidence_graph
from src.recursive_convergence import RecursiveConvergenceRun


@dataclass(frozen=True)
class ReplayComparison:
    original_graph_id: str
    replay_graph_id: str
    graph_match: bool
    run_match: bool
    artifact_match: bool
    original_cycles: int
    replay_cycles: int
    version: int = 1

    @property
    def deterministic(self) -> bool:
        return self.graph_match and self.run_match and self.artifact_match

    def as_dict(self) -> dict:
        return asdict(self) | {"deterministic": self.deterministic}


def compare_recursive_replay(
    original: RecursiveConvergenceRun,
    replay: RecursiveConvergenceRun,
) -> ReplayComparison:
    """Compare two immutable recursive runs without mutating either run."""
    if not isinstance(original, RecursiveConvergenceRun):
        raise TypeError("original must be RecursiveConvergenceRun")
    if not isinstance(replay, RecursiveConvergenceRun):
        raise TypeError("replay must be RecursiveConvergenceRun")

    original_graph = build_evidence_graph(original)
    replay_graph = build_evidence_graph(replay)

    original_artifacts = tuple(
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
        for cycle in original.cycles
    )
    replay_artifacts = tuple(
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
        for cycle in replay.cycles
    )

    return ReplayComparison(
        original_graph_id=original_graph.id,
        replay_graph_id=replay_graph.id,
        graph_match=original_graph == replay_graph,
        run_match=original == replay,
        artifact_match=original_artifacts == replay_artifacts,
        original_cycles=original.cycle_count,
        replay_cycles=replay.cycle_count,
    )


__all__ = ["ReplayComparison", "compare_recursive_replay"]
