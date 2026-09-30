"""Collective Computation Runtime MVP for theNet v2.7."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from src.agent_state import AgentState
from src.commit import EvolutionCommit, create_evolution_commit
from src.consensus import Consensus, create_consensus
from src.evolution import evolve_agent_state
from src.evolution_guard import ensure_not_replayed
from src.gamma import Convergence, create_convergence
from src.memory import MemoryRecord, create_memory
from src.omega_credit import OmegaCredit, create_omega_credit_from_utility
from src.omega_credit_allocation import create_omega_credit_allocation
from src.phi import PhiStructure, create_phi
from src.phi_coherence import phi_coherence
from src.proposal import Proposal
from src.relational_utility import RelationalUtility, create_relational_utility
from src.relation import Relation, create_relation
from src.resource_state import ResourceState
from src.verification import Verification
from src.contribution_ledger import ContributionLedger, create_contribution_ledger
from src.execution_ledger import ExecutionRecord, create_execution_record
from src.outcome import ComputationOutcome, create_computation_outcome
from src.omega_credit_resource_commitment import apply_omega_credit_allocation


@dataclass(frozen=True)
class CollectiveComputationResult:
    consensus: Consensus
    convergence: Convergence
    commit: EvolutionCommit
    execution: ExecutionRecord
    outcome: ComputationOutcome
    memory: MemoryRecord
    relations: tuple[Relation, ...]
    phi: PhiStructure
    utility: RelationalUtility
    credit: OmegaCredit
    contribution_ledger: ContributionLedger
    memory_resource: ResourceState
    compute_resource: ResourceState
    state: AgentState


def run_collective_computation(
    current_state: AgentState,
    proposal: Proposal,
    verifications: Iterable[Verification],
    quorum: int,
    new_singularity_id: str,
    created_at: str,
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    executor: Callable[[Proposal], str],
    *,
    utility: float = 1.0,
    prior_commits: Iterable[EvolutionCommit] = (),
) -> CollectiveComputationResult:
    """Run one proposal-to-outcome-to-state cycle.

    The executor is the sandbox boundary. It receives only the immutable
    proposal and returns a measured result string. Canonical state is not
    advanced until consensus, execution, outcome, contribution and resource
    provenance have been constructed.
    """
    if not isinstance(current_state, AgentState):
        raise TypeError("current_state must be AgentState")
    if not isinstance(proposal, Proposal):
        raise TypeError("proposal must be Proposal")
    if not isinstance(memory_resource, ResourceState):
        raise TypeError("memory_resource must be ResourceState")
    if not isinstance(compute_resource, ResourceState):
        raise TypeError("compute_resource must be ResourceState")
    if not callable(executor):
        raise TypeError("executor must be callable")

    proposer_ids = {current_state.id, current_state.subject_id}
    if proposal.proposer_id not in proposer_ids:
        raise ValueError("proposal proposer must match current_state")
    if proposal.base_state_id != current_state.id:
        raise ValueError("proposal does not target current state")

    records = tuple(verifications)
    if any(item.verifier_id in proposer_ids for item in records):
        raise ValueError("proposer cannot verify its own proposal")

    consensus = create_consensus(proposal.id, records, quorum)
    if not consensus.reached:
        raise ValueError("collective quorum has not been reached")

    convergence = create_convergence([proposal.id])

    relations = tuple(
        create_relation(
            current_state.subject_id,
            verification.verifier_id,
            "verified",
            created_at,
        )
        for verification in records
    )
    if not relations:
        raise ValueError("collective computation requires verifier relations")
    phi = create_phi(relations)

    result = executor(proposal)
    if not isinstance(result, str):
        raise TypeError("executor must return a string result")
    outcome = create_computation_outcome(
        proposal.id,
        result,
        True,
        utility,
        created_at,
    )

    memory = create_memory(
        current_state.subject_id,
        outcome.id,
        "collective-computation-outcome",
        created_at,
    )
    relational_utility = create_relational_utility(
        current_state.subject_id,
        outcome.utility,
        [outcome.id, memory.id],
        True,
        created_at,
    )

    remaining_memory = max(memory_resource.available - memory_resource.used, 0.0)
    remaining_compute = max(compute_resource.available - compute_resource.used, 0.0)
    memory_efficiency = 1.0 - memory_resource.efficiency
    compute_efficiency = 1.0 - compute_resource.efficiency
    resource_efficiency = (memory_efficiency + compute_efficiency) / 2.0
    coherence = phi_coherence(phi)

    credit = create_omega_credit_from_utility(
        relational_utility,
        resource_efficiency=resource_efficiency,
        coherence=coherence,
        created_at=created_at,
    )
    contribution_ledger = create_contribution_ledger([credit])
    allocation = create_omega_credit_allocation(
        _distribution(contribution_ledger, credit),
        remaining_memory,
        remaining_compute,
    )
    memory_after, compute_after = apply_omega_credit_allocation(
        allocation,
        memory_resource,
        compute_resource,
        created_at,
    )

    execution = create_execution_record(
        contribution_ledger_id=contribution_ledger.id,
        allocation_id=allocation.id,
        memory_before_id=memory_resource.id,
        memory_after_id=memory_after.id,
        compute_before_id=compute_resource.id,
        compute_after_id=compute_after.id,
        memory_by_contributor=allocation.memory_by_contributor,
        compute_by_contributor=allocation.compute_by_contributor,
        created_at=created_at,
    )

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

    return CollectiveComputationResult(
        consensus=consensus,
        convergence=convergence,
        commit=commit,
        execution=execution,
        outcome=outcome,
        memory=memory,
        relations=relations,
        phi=phi,
        utility=relational_utility,
        credit=credit,
        contribution_ledger=contribution_ledger,
        memory_resource=memory_after,
        compute_resource=compute_after,
        state=state,
    )


def _distribution(
    ledger: ContributionLedger,
    credit: OmegaCredit,
):
    from src.omega_credit_engine import create_omega_credit_distribution_from_ledger

    if credit.id not in ledger.entries:
        raise ValueError("credit is missing from contribution ledger")
    return create_omega_credit_distribution_from_ledger(ledger)


__all__ = ["CollectiveComputationResult", "run_collective_computation"]
