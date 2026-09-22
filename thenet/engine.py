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
from src.meaning import Meaning, create_meaning
from src.omega import OmegaTransition, create_omega_transition
from src.omega2 import OmegaMemory, create_omega_memory
from src.phi import PhiStructure, create_phi
from src.proposal import Proposal, create_proposal
from src.relation import Relation, create_relation
from src.resonance import Resonance, create_resonance
from src.self_knowledge import SelfKnowledge, create_self_knowledge
from src.singularity import Singularity, create_singularity
from src.verification import Verification, create_verification


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
    omega = create_omega_transition(
        phi.id,
        source.id,
        "verified structural evolution",
        created_at,
    )
    omega2 = create_omega_memory(omega.id, source.id, created_at)
    resonance = create_resonance(phi.id, omega2.id, created_at)

    proposal = create_proposal(
        source.id,
        source.id,
        proposal_text,
        created_at,
    )
    verification = create_verification(
        proposal.id,
        target.id,
        evidence,
        True,
        created_at,
    )
    gamma = create_convergence([proposal.id])
    pi = create_meaning(gamma.id, relation.id, created_at)
    psi = create_expression(pi.id, expression_id, created_at)
    theta = create_self_knowledge(source.id, phi.id, omega2.id, created_at)
    rho = create_co_definition(source.id, target.id, relation_kind, created_at)
    sigma = create_essence([relation.id])

    iota = create_singularity(
        phi.id,
        omega.id,
        omega2.id,
        resonance.id,
        gamma.id,
        pi.id,
        psi.id,
        theta.id,
        rho.id,
        sigma.id,
        created_at,
    )
    agent_state = create_agent_state(source.id, iota.id, created_at)

    return GenesisClosure(
        source=source,
        target=target,
        relation=relation,
        phi=phi,
        omega=omega,
        omega2=omega2,
        resonance=resonance,
        proposal=proposal,
        verification=verification,
        gamma=gamma,
        pi=pi,
        psi=psi,
        theta=theta,
        rho=rho,
        sigma=sigma,
        iota=iota,
        agent_state=agent_state,
    )


def advance(
    current_state: AgentState,
    proposal: Proposal,
    verification: Verification,
    convergence: Convergence,
    new_singularity_id: str,
    created_at: str,
) -> AgentState:
    commit: EvolutionCommit = create_evolution_commit(
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
    return evolve_agent_state(
        current_state,
        commit,
        new_singularity_id,
        created_at,
    )


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
        current_state,
        proposal,
        verifications,
        quorum,
        new_singularity_id,
        created_at,
    )
