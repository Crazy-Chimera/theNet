"""Immutable Genesis bootstrap consensus policy."""

from __future__ import annotations

from dataclasses import dataclass

from src.genesis_majority_quorum import genesis_majority_quorum


@dataclass(frozen=True)
class GenesisBootstrapPolicy:
    population_size: int
    proposer_count: int
    eligible_verifier_count: int
    quorum: int
    collective_learning_possible: bool


def derive_genesis_bootstrap_policy(population_size: int) -> GenesisBootstrapPolicy:
    if (
        not isinstance(population_size, int)
        or isinstance(population_size, bool)
        or population_size < 1
    ):
        raise ValueError("population_size must be a positive integer")

    eligible_verifiers = population_size - 1

    if eligible_verifiers == 0:
        return GenesisBootstrapPolicy(
            population_size=population_size,
            proposer_count=1,
            eligible_verifier_count=0,
            quorum=0,
            collective_learning_possible=False,
        )

    quorum = genesis_majority_quorum(population_size)

    return GenesisBootstrapPolicy(
        population_size=population_size,
        proposer_count=1,
        eligible_verifier_count=eligible_verifiers,
        quorum=quorum,
        collective_learning_possible=True,
    )
