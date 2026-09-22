"""Genesis learning facade using the strict-majority quorum policy."""

from __future__ import annotations

from src.genesis_learning import GenesisLearningRun, simulate_genesis_learning
from src.genesis_majority_quorum import genesis_majority_quorum
from src.genesis_population import GenesisPopulation


def simulate_genesis_majority_learning(
    population: GenesisPopulation,
    proposal_texts: tuple[str, ...],
    created_at: tuple[str, ...],
) -> GenesisLearningRun:
    """Run Genesis learning with a quorum derived from population size."""
    quorum = genesis_majority_quorum(len(population.agents))
    return simulate_genesis_learning(
        population,
        proposal_texts,
        quorum=quorum,
        created_at=created_at,
    )
