"""Deterministic convergence metrics for theNet F10.

These metrics evaluate runtime structure and verified invariants. They are
project-level operational metrics, not claims about physical reality.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
import math

from src.agent_state import AgentState
from src.commit import EvolutionCommit
from src.consensus import Consensus
from src.gamma import Convergence
from src.memory import MemoryRecord
from src.outcome import ComputationOutcome
from src.phi import PhiStructure
from src.phi_coherence import phi_coherence
from src.relational_utility import RelationalUtility


K_THRESHOLD = 0.8
C_THRESHOLD = 0.3
R_THRESHOLD = 5
PHI_THRESHOLD = 0.7


@dataclass(frozen=True)
class ConvergenceMetrics:
    """Operational F10 metrics for one verified computation cycle."""

    k: float
    c: float
    r: int
    phi: float
    invariant_checks: tuple[bool, ...]
    recursive_chain: tuple[str, ...]
    converged: bool
    version: int = 1

    @property
    def passed(self) -> bool:
        return self.converged


def _unit(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be finite and in [0, 1]")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{name} must be finite and in [0, 1]")
    return normalized


def _complexity(candidate_count: int, node_count: int, edge_count: int) -> float:
    """Measure excess branching/redundancy over a minimal connected path.

    C=0 is a minimal single-candidate connected structure. Increasing C means
    additional candidate branching or edges beyond a spanning connection.
    This is deliberately a structural proxy, not a universal complexity law.
    """
    if candidate_count < 1 or node_count < 1 or edge_count < 0:
        raise ValueError("invalid structural counts")

    excess_candidates = max(candidate_count - 1, 0)
    minimal_edges = max(node_count - 1, 0)
    excess_edges = max(edge_count - minimal_edges, 0)
    denominator = candidate_count + minimal_edges + max(edge_count, 1)
    return min(1.0, (excess_candidates + excess_edges) / denominator)


def measure_convergence_metrics(
    *,
    current_state: AgentState,
    next_state: AgentState,
    consensus: Consensus,
    convergence: Convergence,
    commit: EvolutionCommit,
    outcome: ComputationOutcome,
    memory: MemoryRecord,
    utility: RelationalUtility,
    phi: PhiStructure,
) -> ConvergenceMetrics:
    """Measure F10 from independently constructed runtime artifacts."""
    if not isinstance(current_state, AgentState):
        raise TypeError("current_state must be AgentState")
    if not isinstance(next_state, AgentState):
        raise TypeError("next_state must be AgentState")
    if not isinstance(consensus, Consensus):
        raise TypeError("consensus must be Consensus")
    if not isinstance(convergence, Convergence):
        raise TypeError("convergence must be Convergence")
    if not isinstance(commit, EvolutionCommit):
        raise TypeError("commit must be EvolutionCommit")
    if not isinstance(outcome, ComputationOutcome):
        raise TypeError("outcome must be ComputationOutcome")
    if not isinstance(memory, MemoryRecord):
        raise TypeError("memory must be MemoryRecord")
    if not isinstance(utility, RelationalUtility):
        raise TypeError("utility must be RelationalUtility")
    if not isinstance(phi, PhiStructure):
        raise TypeError("phi must be PhiStructure")

    checks = (
        consensus.reached,
        convergence.converged,
        convergence.resolved_id == commit.proposal_id,
        outcome.success,
        utility.verified,
        outcome.id == memory.source_id,
        utility.evidence_ids == tuple(sorted((outcome.id, memory.id))),
        commit.previous_state_id == current_state.id,
        next_state.version == current_state.version + 1,
    )
    k = sum(checks) / len(checks)

    c = _complexity(
        len(convergence.candidate_states),
        phi.node_count,
        phi.edge_count,
    )

    chain = (
        current_state.id,
        commit.proposal_id,
        consensus.id,
        convergence.id,
        outcome.id,
        utility.id,
        memory.id,
        commit.id,
        next_state.id,
    )
    if len(set(chain)) != len(chain):
        raise ValueError("recursive chain must contain unique artifacts")

    r = len(chain) - 1
    phi_value = _unit(phi_coherence(phi), "phi")

    converged = (
        k > K_THRESHOLD
        and c < C_THRESHOLD
        and r > R_THRESHOLD
        and phi_value > PHI_THRESHOLD
    )

    return ConvergenceMetrics(
        k=k,
        c=c,
        r=r,
        phi=phi_value,
        invariant_checks=checks,
        recursive_chain=chain,
        converged=converged,
    )


__all__ = [
    "C_THRESHOLD",
    "ConvergenceMetrics",
    "K_THRESHOLD",
    "PHI_THRESHOLD",
    "R_THRESHOLD",
    "measure_convergence_metrics",
]
