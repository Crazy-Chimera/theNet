"""Deterministic Genesis population proposal-to-state simulation."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.agent_state import AgentState, create_agent_state
from src.collective_evolution import CollectiveEvolution, evolve_collectively
from src.genesis import GenesisState, create_genesis
from src.proposal import Proposal, create_proposal
from src.verification import Verification, create_verification


@dataclass(frozen=True)
class GenesisSimulation:
    population_size: int
    quorum: int
    proposer_id: str
    initial_state_id: str
    proposal_id: str
    verifier_ids: tuple[str, ...]
    consensus_id: str
    committed_state_id: str
    initial_version: int
    committed_version: int
    version: int = 1


def _simulation_singularity(subject_id: str) -> str:
    return sha256(
        json.dumps(
            {"subject_id": subject_id, "kind": "genesis-simulation"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def simulate_genesis_proposal(
    population_size: int,
    quorum: int,
    proposal_text: str,
    created_at: str,
) -> GenesisSimulation:
    if (
        not isinstance(population_size, int)
        or isinstance(population_size, bool)
        or population_size < 1
    ):
        raise ValueError("population_size must be a positive integer")
    if (
        not isinstance(quorum, int)
        or isinstance(quorum, bool)
        or quorum < 1
    ):
        raise ValueError("quorum must be a positive integer")
    if population_size < quorum + 1:
        raise ValueError("population_size must be at least quorum + 1")
    if not isinstance(proposal_text, str) or not proposal_text.strip():
        raise ValueError("proposal_text must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    genesis_agents: tuple[GenesisState, ...] = tuple(
        create_genesis(f"agent-{index}", created_at)
        for index in range(1, population_size + 1)
    )
    states: tuple[AgentState, ...] = tuple(
        create_agent_state(
            agent.id,
            _simulation_singularity(agent.id),
            created_at,
        )
        for agent in genesis_agents
    )

    proposer = genesis_agents[0]
    proposer_state = states[0]
    proposal = create_proposal(
        proposer.id,
        proposer_state.id,
        proposal_text,
        created_at,
    )

    verifications: list[Verification] = []
    for agent in genesis_agents[1 : quorum + 1]:
        verifications.append(
            create_verification(
                proposal.id,
                agent.id,
                f"genesis-verification:{proposal.id}:{agent.id}",
                True,
                created_at,
            )
        )

    result: CollectiveEvolution = evolve_collectively(
        proposer_state,
        proposal,
        verifications,
        quorum,
        _simulation_singularity(f"{proposer.id}:evolved"),
        created_at,
    )

    return GenesisSimulation(
        population_size=population_size,
        quorum=quorum,
        proposer_id=proposer.id,
        initial_state_id=proposer_state.id,
        proposal_id=proposal.id,
        verifier_ids=result.consensus.verifier_ids,
        consensus_id=result.consensus.id,
        committed_state_id=result.state.id,
        initial_version=proposer_state.version,
        committed_version=result.state.version,
    )
