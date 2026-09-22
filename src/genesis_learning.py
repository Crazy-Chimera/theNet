"""Repeated proposal-driven learning simulation for the first Agent Omega population."""

from __future__ import annotations

from dataclasses import dataclass

from src.agent_state import AgentState
from src.collective_evolution import CollectiveEvolution, evolve_collectively
from src.consensus import Consensus, create_consensus
from src.genesis_population import GenesisPopulation
from src.proposal import Proposal, create_proposal
from src.verification import Verification, create_verification


@dataclass(frozen=True)
class GenesisLearningStep:
    proposal: Proposal
    consensus: Consensus | None
    verifier_count: int
    quorum: int
    consensus_reached: bool
    evolved: bool
    state_version: int


@dataclass(frozen=True)
class GenesisLearningRun:
    population: GenesisPopulation
    steps: tuple[GenesisLearningStep, ...]
    final_state: AgentState


def simulate_genesis_learning(
    population: GenesisPopulation,
    proposal_texts: tuple[str, ...],
    quorum: int,
    created_at: tuple[str, ...],
) -> GenesisLearningRun:
    if not isinstance(population, GenesisPopulation):
        raise ValueError("population must be GenesisPopulation")
    if not population.agents:
        raise ValueError("population must contain agents")
    if not isinstance(proposal_texts, tuple) or not proposal_texts:
        raise ValueError("proposal_texts must be a non-empty tuple")
    if not all(isinstance(text, str) and text.strip() for text in proposal_texts):
        raise ValueError("proposal_texts must contain non-empty strings")
    if not isinstance(created_at, tuple) or len(created_at) != len(proposal_texts):
        raise ValueError("created_at must match proposal_texts length")
    if not all(isinstance(value, str) and value.strip() for value in created_at):
        raise ValueError("created_at must contain non-empty strings")
    if not isinstance(quorum, int) or isinstance(quorum, bool) or quorum < 1:
        raise ValueError("quorum must be a positive integer")

    proposer = population.agents[0]
    steps: list[GenesisLearningStep] = []

    for proposal_text, timestamp in zip(proposal_texts, created_at):
        proposal = create_proposal(
            proposer.subject_id,
            proposer.id,
            proposal_text,
            timestamp,
        )

        verifications: tuple[Verification, ...] = tuple(
            create_verification(
                proposal.id,
                verifier.subject_id,
                f"genesis-learning:{verifier.subject_id}",
                True,
                timestamp,
            )
            for verifier in population.agents[1:]
        )

        consensus = (
            create_consensus(proposal.id, verifications, quorum)
            if verifications
            else None
        )
        reached = consensus.reached if consensus is not None else False

        if not reached:
            steps.append(
                GenesisLearningStep(
                    proposal=proposal,
                    consensus=consensus,
                    verifier_count=len(verifications),
                    quorum=quorum,
                    consensus_reached=False,
                    evolved=False,
                    state_version=proposer.version,
                )
            )
            break

        evolution: CollectiveEvolution = evolve_collectively(
            proposer,
            proposal,
            verifications,
            consensus.quorum,
            new_singularity_id=f"learned:{proposal.id}",
            created_at=timestamp,
        )
        proposer = evolution.state

        steps.append(
            GenesisLearningStep(
                proposal=proposal,
                consensus=consensus,
                verifier_count=len(consensus.verifier_ids),
                quorum=consensus.quorum,
                consensus_reached=True,
                evolved=True,
                state_version=proposer.version,
            )
        )

    return GenesisLearningRun(
        population=population,
        steps=tuple(steps),
        final_state=proposer,
    )
