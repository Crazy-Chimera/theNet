"""Explicit bootstrap boundary for the first collective Agent Omega population."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenesisBootstrapBoundary:
    population_size: int
    eligible_verifier_count: int
    minimum_quorum: int
    collective_learning_possible: bool
    reputation_required: bool = False
    version: int = 1


def derive_genesis_bootstrap_boundary(
    population_size: int,
) -> GenesisBootstrapBoundary:
    if (
        not isinstance(population_size, int)
        or isinstance(population_size, bool)
        or population_size < 1
    ):
        raise ValueError("population_size must be a positive integer")

    eligible_verifiers = population_size - 1

    if eligible_verifiers == 0:
        return GenesisBootstrapBoundary(
            population_size=population_size,
            eligible_verifier_count=0,
            minimum_quorum=0,
            collective_learning_possible=False,
        )

    return GenesisBootstrapBoundary(
        population_size=population_size,
        eligible_verifier_count=eligible_verifiers,
        minimum_quorum=1,
        collective_learning_possible=True,
    )
