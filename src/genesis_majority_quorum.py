"""Genesis-specific strict-majority quorum policy."""

from __future__ import annotations

from src.consensus import strict_majority_quorum


def genesis_majority_quorum(population_size: int) -> int:
    """Return strict-majority quorum among independent non-proposer agents."""
    if (
        not isinstance(population_size, int)
        or isinstance(population_size, bool)
        or population_size < 1
    ):
        raise ValueError("population_size must be a positive integer")

    eligible_verifiers = population_size - 1
    if eligible_verifiers < 1:
        raise ValueError("Genesis requires at least one independent verifier")

    return strict_majority_quorum(eligible_verifiers)
