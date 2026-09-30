"""Agent Ω decision-cycle orchestration boundary for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.agent_state import AgentState
from src.essence import Essence, create_essence
from src.genesis import create_genesis
from src.gamma import Convergence, create_convergence
from src.identity import Identity, IdentityVault, Signature
from src.memory import MemoryRecord, create_memory
from src.meaning import Meaning, create_meaning
from src.omega import OmegaTransition, create_omega_transition
from src.omega2 import OmegaMemory, create_omega_memory
from src.phi import PhiStructure, create_phi
from src.proposal import Proposal
from src.relation import Relation
from src.self_knowledge import SelfKnowledge, create_self_knowledge


@dataclass(frozen=True)
class DecisionCycle:
    theta: SelfKnowledge
    sigma: Essence
    gamma: Convergence
    omega: OmegaTransition
    pi: Meaning
    omega2: OmegaMemory
    input_memory: MemoryRecord
    proposal_signature: Signature | None
    identity_verified: bool
    order: tuple[str, ...] = ("THETA", "SIGMA", "GAMMA", "OMEGA", "PI", "OMEGA2")
    version: int = 1


def _memory_seed(state: AgentState, proposal: Proposal, created_at: str) -> MemoryRecord:
    return create_memory(
        state.subject_id,
        sha256(
            json.dumps(
                {
                    "proposal_id": proposal.id,
                    "state_id": state.id,
                    "created_at": created_at,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "decision-input",
        created_at,
    )


def run_decision_cycle(
    state: AgentState,
    proposal: Proposal,
    relations: tuple[Relation, ...] | list[Relation],
    created_at: str,
    *,
    identity: Identity | None = None,
    vault: IdentityVault | None = None,
    password: str | None = None,
) -> DecisionCycle:
    if not isinstance(state, AgentState):
        raise TypeError("state must be AgentState")
    if not isinstance(proposal, Proposal):
        raise TypeError("proposal must be Proposal")
    if proposal.base_state_id != state.id:
        raise ValueError("proposal must target current state")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    relation_records = tuple(relations)
    if not relation_records:
        raise ValueError("decision cycle requires at least one relation")
    if any(not isinstance(relation, Relation) for relation in relation_records):
        raise TypeError("relations must contain Relation objects")

    phi: PhiStructure = create_phi(relation_records)
    input_memory = _memory_seed(state, proposal, created_at)

    # Θ — self-model of the current relational state.
    theta = create_self_knowledge(
        state.subject_id,
        phi.id,
        input_memory.id,
        created_at,
    )

    # Σ — relational ground of the current context.
    sigma = create_essence([relation.id for relation in relation_records])

    # Γ — convergence target of the proposal.
    gamma = create_convergence([proposal.id])

    # Ω — proposed state transition; canonical state remains unchanged.
    omega = create_omega_transition(
        state.id,
        proposal.id,
        proposal.proposal,
        created_at,
    )

    # Π — meaning/contribution associated with convergence.
    pi = create_meaning(gamma.id, relation_records[0].id, created_at)

    # Ω² — memory trace of the proposed transition.
    omega2 = create_omega_memory(omega.id, state.id, created_at)

    signature = None
    identity_verified = False
    if identity is not None or vault is not None or password is not None:
        if not isinstance(identity, Identity):
            raise TypeError("identity is required for identity-bound cycles")
        if not isinstance(vault, IdentityVault):
            raise TypeError("vault is required for identity-bound cycles")
        if not isinstance(password, str) or not password:
            raise ValueError("password is required for identity-bound cycles")
        if proposal.proposer_id not in {identity.did, state.subject_id}:
            raise ValueError("identity does not match proposal proposer")
        signature = vault.sign(identity.did, proposal.id, password)
        identity_verified = vault.verify(identity, proposal.id, signature)

    return DecisionCycle(
        theta=theta,
        sigma=sigma,
        gamma=gamma,
        omega=omega,
        pi=pi,
        omega2=omega2,
        input_memory=input_memory,
        proposal_signature=signature,
        identity_verified=identity_verified,
    )


__all__ = ["DecisionCycle", "run_decision_cycle"]
