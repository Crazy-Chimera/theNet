"""Deterministic Genesis population simulation for Agent Ω."""

from __future__ import annotations

from dataclasses import dataclass

from src.agent_state import AgentState, create_agent_state
from src.collective_evolution import CollectiveEvolution, evolve_collectively
from src.genesis import create_genesis
from src.proposal import Proposal, create_proposal
from src.singularity import create_singularity
from src.verification import Verification, create_verification


@dataclass(frozen=True)
class GenesisPopulation:
    agents: tuple[AgentState, ...]


@dataclass(frozen=True)
class GenesisProposalRun:
    population: GenesisPopulation
    proposal: Proposal
    verifications: tuple[Verification, ...]
    evolution: CollectiveEvolution | None
    quorum_reached: bool


def create_genesis_population(size: int, created_at: str) -> GenesisPopulation:
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise ValueError("size must be a positive integer")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    agents = []
    for index in range(size):
        genesis = create_genesis(f"genesis-agent-{index}", created_at)
        singularity = create_singularity(
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            genesis.id,
            created_at,
        )
        agents.append(create_agent_state(genesis.id, singularity.id, created_at))

    return GenesisPopulation(agents=tuple(agents))


def simulate_genesis_proposal(
    population: GenesisPopulation,
    proposal_text: str,
    quorum: int,
    created_at: str,
) -> GenesisProposalRun:
    if not isinstance(population, GenesisPopulation):
        raise ValueError("population must be GenesisPopulation")
    if not population.agents:
        raise ValueError("population must contain agents")
    if not isinstance(proposal_text, str) or not proposal_text.strip():
        raise ValueError("proposal_text must be non-empty")

    proposer = population.agents[0]
    proposal = create_proposal(
        proposer.subject_id,
        proposer.id,
        proposal_text,
        created_at,
    )

    verifications = tuple(
        create_verification(
            proposal.id,
            verifier.subject_id,
            f"genesis-verification:{verifier.subject_id}",
            True,
            created_at,
        )
        for verifier in population.agents[1:]
    )

    available = len(verifications)
    quorum_reached = available >= quorum
    evolution = None

    if quorum_reached:
        evolution = evolve_collectively(
            proposer,
            proposal,
            verifications,
            quorum,
            new_singularity_id=f"evolved:{proposal.id}",
            created_at=created_at,
        )

    return GenesisProposalRun(
        population=population,
        proposal=proposal,
        verifications=verifications,
        evolution=evolution,
        quorum_reached=quorum_reached,
    )
