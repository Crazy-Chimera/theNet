"""Genesis learning facade using the explicit bootstrap policy."""

from __future__ import annotations

from src.genesis_bootstrap_policy import derive_genesis_bootstrap_policy
from src.genesis_learning import GenesisLearningRun, simulate_genesis_learning
from src.genesis_population import GenesisPopulation


def simulate_genesis_majority_learning(
    population: GenesisPopulation,
    proposal_texts: tuple[str, ...],
    created_at: tuple[str, ...],
) -> GenesisLearningRun:
    """Run Genesis learning with quorum derived from the bootstrap policy."""
    policy = derive_genesis_bootstrap_policy(len(population.agents))
    if not policy.collective_learning_possible:
        raise ValueError("Genesis requires at least one independent verifier")

    return simulate_genesis_learning(
        population,
        proposal_texts,
        quorum=policy.quorum,
        created_at=created_at,
    )
