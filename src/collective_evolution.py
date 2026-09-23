"""Collective proposal-to-state evolution for Agent Ω."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.evolution_guard import ensure_not_replayed

from src.agent_state import AgentState
from src.commit import EvolutionCommit, create_evolution_commit
from src.consensus import Consensus, create_consensus
from src.evolution import evolve_agent_state
from src.gamma import Convergence, create_convergence
from src.proposal import Proposal
from src.verification import Verification


@dataclass(frozen=True)
class CollectiveEvolution:
    consensus: Consensus
    convergence: Convergence
    commit: EvolutionCommit
    state: AgentState


def evolve_collectively(
    current_state: AgentState,
    proposal: Proposal,
    verifications: Iterable[Verification],
    quorum: int,
    new_singularity_id: str,
    created_at: str,
    prior_commits: Iterable[EvolutionCommit] = (),
) -> CollectiveEvolution:
    if not isinstance(current_state, AgentState):
        raise ValueError("current_state must be AgentState")
    if not isinstance(proposal, Proposal):
        raise ValueError("proposal must be Proposal")

    proposer_ids = {current_state.id, current_state.subject_id}
    if proposal.proposer_id not in proposer_ids:
        raise ValueError("proposal proposer must match current_state")

    records = tuple(verifications)
    if any(verification.verifier_id in proposer_ids for verification in records):
        raise ValueError("proposer cannot verify its own proposal")

    consensus = create_consensus(proposal.id, records, quorum)
    if not consensus.reached:
        raise ValueError("collective quorum has not been reached")

    convergence = create_convergence([proposal.id])
    commit = create_evolution_commit(
        current_state_id=current_state.id,
        proposal_id=proposal.id,
        proposal_base_state_id=proposal.base_state_id,
        verification_ids=consensus.verification_ids,
        all_verifications_valid=True,
        convergence_id=convergence.id,
        converged=convergence.converged,
        resolved_id=convergence.resolved_id,
        created_at=created_at,
    )
    ensure_not_replayed(commit, prior_commits)

    state = evolve_agent_state(
        current_state,
        commit,
        new_singularity_id,
        created_at,
    )
    return CollectiveEvolution(
        consensus=consensus,
        convergence=convergence,
        commit=commit,
        state=state,
    )
