"""End-to-end deterministic Agent Ω collective computation cycle."""

from __future__ import annotations

from dataclasses import dataclass

from src.agent_state import AgentState
from src.collective_evolution import CollectiveEvolution, evolve_collectively
from src.memory import MemoryRecord, create_memory
from src.phi import PhiStructure, create_phi
from src.relational_utility import RelationalUtility, create_relational_utility
from src.relation import Relation, create_relation
from src.resource_state import ResourceState
from src.omega_credit_phi_resource_commitment import (
    commit_self_organizing_allocation_from_phi,
)
from src.proposal import Proposal
from src.verification import Verification


@dataclass(frozen=True)
class CollectiveComputationCycle:
    evolution: CollectiveEvolution
    memory: MemoryRecord
    relations: tuple[Relation, ...]
    phi: PhiStructure
    utility: RelationalUtility
    memory_resource: ResourceState
    compute_resource: ResourceState


def run_collective_computation_cycle(
    current_state: AgentState,
    proposal: Proposal,
    verifications: tuple[Verification, ...],
    quorum: int,
    new_singularity_id: str,
    created_at: str,
    memory_resource: ResourceState,
    compute_resource: ResourceState,
) -> CollectiveComputationCycle:
    evolution = evolve_collectively(
        current_state,
        proposal,
        verifications,
        quorum,
        new_singularity_id,
        created_at,
    )

    verifier_relations = tuple(
        create_relation(
            current_state.subject_id,
            verification.verifier_id,
            "verified",
            created_at,
        )
        for verification in verifications
    )
    if not verifier_relations:
        raise ValueError("collective computation requires verifier relations")

    phi = create_phi(verifier_relations)
    memory = create_memory(
        current_state.subject_id,
        evolution.commit.id,
        "verified-evolution",
        created_at,
    )
    utility = create_relational_utility(
        current_state.subject_id,
        1.0,
        [memory.id],
        True,
        created_at,
    )

    next_memory, next_compute = commit_self_organizing_allocation_from_phi(
        [utility],
        memory_resource,
        compute_resource,
        {current_state.subject_id: phi},
        created_at,
    )

    return CollectiveComputationCycle(
        evolution=evolution,
        memory=memory,
        relations=verifier_relations,
        phi=phi,
        utility=utility,
        memory_resource=next_memory,
        compute_resource=next_compute,
    )
