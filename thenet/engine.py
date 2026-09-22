"""Agent Ω MVP orchestration over theNet immutable primitives."""

from __future__ import annotations

from dataclasses import dataclass

from src.agent_state import AgentState, create_agent_state
from src.co_definition import RelationalCoDefinition, create_co_definition
from src.collective_evolution import CollectiveEvolution, evolve_collectively
from src.commit import EvolutionCommit, create_evolution_commit
from src.essence import Essence, create_essence
from src.evolution import evolve_agent_state
from src.expression import Expression, create_expression
from src.gamma import Convergence, create_convergence
from src.genesis import GenesisState, create_genesis
from src.genesis_quorum_analysis import GenesisQuorumAnalysis, analyze_genesis_quorum
from src.genesis_simulation import (
    GenesisSimulation,
    simulate_genesis_bootstrap,
    simulate_genesis_proposal,
)
from src.genesis_learning import GenesisLearningRun
from src.genesis_majority_learning import simulate_genesis_majority_learning
from src.genesis_population import GenesisPopulation
from src.meaning import Meaning, create_meaning
from src.omega import OmegaTransition, create_omega_transition
from src.omega2 import OmegaMemory, create_omega_memory
from src.omega_credit import OmegaCredit
from src.omega_credit_allocation import OmegaCreditAllocation
from src.omega_credit_resource_commitment import apply_omega_credit_allocation
from src.omega_credit_runtime import allocate_omega_credit_resources as _allocate_omega_credit_resources
from src.omega_credit_engine import (
    OmegaCreditDistribution,
    create_omega_credit_distribution,
)
from src.phi import PhiStructure, create_phi
from src.phi_derived_allocation import allocate_memory_and_compute_from_phi
from src.proposal import Proposal, create_proposal
from src.relation import Relation, create_relation
from src.resonance import Resonance, create_resonance
from src.self_knowledge import SelfKnowledge, create_self_knowledge
from src.singularity import Singularity, create_singularity
from src.verification import Verification, create_verification
from src.relational_utility import RelationalUtility
from src.contribution_ledger import ContributionLedger
from src.execution_ledger import ExecutionRecord
from src.execution_audit import ExecutionAudit, create_execution_audit
from src.resource_state import ResourceState
from src.omega_credit_self_organizing_commitment import (
    commit_ledger_backed_allocation_with_record,
    commit_self_organizing_allocation,
)
from src.omega_credit_phi_resource_commitment import commit_self_organizing_allocation_from_phi
from src.self_organizing_allocation import (
    SelfOrganizingAllocation,
    allocate_memory_and_compute,
)


@dataclass(frozen=True)
class GenesisClosure:
    source: GenesisState
    target: GenesisState
    relation: Relation
    phi: PhiStructure
    omega: OmegaTransition
    omega2: OmegaMemory
    resonance: Resonance
    proposal: Proposal
    verification: Verification
    gamma: Convergence
    pi: Meaning
    psi: Expression
    theta: SelfKnowledge
    rho: RelationalCoDefinition
    sigma: Essence
    iota: Singularity
    agent_state: AgentState


def build_closure(
    source_subject: str,
    target_subject: str,
    relation_kind: str,
    proposal_text: str,
    evidence: str,
    expression_id: str,
    created_at: str,
) -> GenesisClosure:
    source = create_genesis(source_subject, created_at)
    target = create_genesis(target_subject, created_at)
    relation = create_relation(source.id, target.id, relation_kind, created_at)
    phi = create_phi([relation])
    omega = create_omega_transition(phi.id, source.id, "verified structural evolution", created_at)
    omega2 = create_omega_memory(omega.id, source.id, created_at)
    resonance = create_resonance(phi.id, omega2.id, created_at)
    proposal = create_proposal(source.id, source.id, proposal_text, created_at)
    verification = create_verification(proposal.id, target.id, evidence, True, created_at)
    gamma = create_convergence([proposal.id])
    pi = create_meaning(gamma.id, relation.id, created_at)
    psi = create_expression(pi.id, expression_id, created_at)
    theta = create_self_knowledge(source.id, phi.id, omega2.id, created_at)
    rho = create_co_definition(source.id, target.id, relation_kind, created_at)
    sigma = create_essence([relation.id])
    iota = create_singularity(
        phi.id, omega.id, omega2.id, resonance.id, gamma.id, pi.id,
        psi.id, theta.id, rho.id, sigma.id, created_at,
    )
    agent_state = create_agent_state(source.id, iota.id, created_at)
    return GenesisClosure(
        source=source, target=target, relation=relation, phi=phi, omega=omega,
        omega2=omega2, resonance=resonance, proposal=proposal,
        verification=verification, gamma=gamma, pi=pi, psi=psi, theta=theta,
        rho=rho, sigma=sigma, iota=iota, agent_state=agent_state,
    )


def advance(
    current_state: AgentState,
    proposal: Proposal,
    verification: Verification,
    convergence: Convergence,
    new_singularity_id: str,
    created_at: str,
) -> AgentState:
    commit = create_evolution_commit(
        current_state_id=current_state.id,
        proposal_id=proposal.id,
        proposal_base_state_id=proposal.base_state_id,
        verification_ids=[verification.id],
        all_verifications_valid=verification.valid,
        convergence_id=convergence.id,
        converged=convergence.converged,
        resolved_id=convergence.resolved_id,
        created_at=created_at,
    )
    return evolve_agent_state(current_state, commit, new_singularity_id, created_at)


def advance_collectively(
    current_state: AgentState,
    proposal: Proposal,
    verifications: list[Verification],
    quorum: int,
    new_singularity_id: str,
    created_at: str,
) -> CollectiveEvolution:
    """Advance an Agent Ω state only after explicit verifier quorum."""
    return evolve_collectively(
        current_state, proposal, verifications, quorum,
        new_singularity_id, created_at,
    )


def allocate_omega_credit_resources(
    distribution: OmegaCreditDistribution,
    memory_capacity: float,
    compute_capacity: float,
) -> OmegaCreditAllocation:
    """Allocate memory and compute from an already aggregated Ω-Credit distribution."""
    return _allocate_omega_credit_resources(
        distribution, memory_capacity, compute_capacity
    )


def commit_omega_credit_resources(
    allocation: OmegaCreditAllocation,
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Apply an Ω-Credit allocation as immutable resource-state transitions."""
    return apply_omega_credit_allocation(
        allocation, memory_resource, compute_resource, created_at
    )


def aggregate_omega_credit(
    credits: list[OmegaCredit],
) -> OmegaCreditDistribution:
    """Aggregate independently produced Ω-Credit records into contribution shares."""
    return create_omega_credit_distribution(credits)


def commit_ledger_backed_resources_with_record(
    ledger: "ContributionLedger",
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    memory_capacity: float,
    compute_capacity: float,
    created_at: str,
) -> tuple[ResourceState, ResourceState, "ExecutionRecord"]:
    """Commit ledger-backed resources and expose immutable provenance."""
    return commit_ledger_backed_allocation_with_record(
        ledger,
        memory_resource,
        compute_resource,
        memory_capacity,
        compute_capacity,
        created_at,
    )


def allocate_resources(
    utilities: list[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    coherence_by_contributor: dict[str, float],
) -> SelfOrganizingAllocation:
    """Allocate from explicitly supplied Φ coherence."""
    return allocate_memory_and_compute(
        utilities, memory_resource, compute_resource, coherence_by_contributor
    )


def commit_self_organizing_resources(
    utilities: list[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    coherence_by_contributor: dict[str, float],
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Expose the canonical Ω-Credit self-organizing resource transition."""
    return commit_self_organizing_allocation(
        tuple(utilities),
        memory_resource,
        compute_resource,
        coherence_by_contributor,
        created_at,
    )


def allocate_resources_from_phi(
    utilities: list[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    structures_by_contributor: dict[str, PhiStructure],
) -> SelfOrganizingAllocation:
    """Derive Φ coherence from topology before allocating resources."""
    return allocate_memory_and_compute_from_phi(
        utilities, memory_resource, compute_resource, structures_by_contributor
    )


def commit_self_organizing_resources_from_phi(
    utilities: list[RelationalUtility],
    memory_resource: ResourceState,
    compute_resource: ResourceState,
    structures_by_contributor: dict[str, PhiStructure],
    created_at: str,
) -> tuple[ResourceState, ResourceState]:
    """Derive Φ coherence and commit the resulting Ω-Credit resource transition."""
    return commit_self_organizing_allocation_from_phi(
        utilities,
        memory_resource,
        compute_resource,
        structures_by_contributor,
        created_at,
    )


def simulate_genesis_agents(
    population_size: int,
    quorum: int,
    proposal_text: str,
    created_at: str,
) -> GenesisSimulation:
    """Run the deterministic Genesis proposal-to-state simulation."""
    return simulate_genesis_proposal(
        population_size, quorum, proposal_text, created_at
    )


def analyze_quorum_capacity(
    population_size: int,
    max_quorum: int,
) -> GenesisQuorumAnalysis:
    """Expose Genesis verifier-capacity analysis through the runtime facade."""
    return analyze_genesis_quorum(population_size, max_quorum)


def simulate_genesis_bootstrap_agents(
    population_size: int,
    proposal_text: str,
    created_at: str,
) -> GenesisSimulation:
    """Run Genesis simulation using the derived bootstrap quorum policy."""
    return simulate_genesis_bootstrap(population_size, proposal_text, created_at)


def simulate_genesis_majority_agents(
    population: GenesisPopulation,
    proposal_texts: tuple[str, ...],
    created_at: tuple[str, ...],
) -> GenesisLearningRun:
    """Run repeated Genesis learning with quorum derived from population size."""
    return simulate_genesis_majority_learning(population, proposal_texts, created_at)


def create_execution_audit_surface(records: list[ExecutionRecord]) -> ExecutionAudit:
    """Create a read-only query surface over immutable execution provenance."""
    return create_execution_audit(tuple(records))


def find_execution_record(
    audit: ExecutionAudit,
    record_id: str,
) -> ExecutionRecord | None:
    """Retrieve one execution record by its immutable identity."""
    return audit.find_record(record_id)


def find_execution_records_by_contribution_ledger(
    audit: ExecutionAudit,
    contribution_ledger_id: str,
) -> tuple[ExecutionRecord, ...]:
    """Retrieve all execution records linked to one contribution ledger."""
    return audit.find_records_by_contribution_ledger(contribution_ledger_id)
