"""Deterministic quorum-capacity analysis for the Genesis population."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenesisQuorumRow:
    quorum: int
    reachable: bool
    required_population: int


@dataclass(frozen=True)
class GenesisQuorumAnalysis:
    population_size: int
    available_verifiers: int
    rows: tuple[GenesisQuorumRow, ...]


def analyze_genesis_quorum(
    population_size: int,
    max_quorum: int,
) -> GenesisQuorumAnalysis:
    if (
        not isinstance(population_size, int)
        or isinstance(population_size, bool)
        or population_size < 1
    ):
        raise ValueError("population_size must be a positive integer")
    if (
        not isinstance(max_quorum, int)
        or isinstance(max_quorum, bool)
        or max_quorum < 1
    ):
        raise ValueError("max_quorum must be a positive integer")

    available_verifiers = population_size - 1
    rows = tuple(
        GenesisQuorumRow(
            quorum=quorum,
            reachable=quorum <= available_verifiers,
            required_population=quorum + 1,
        )
        for quorum in range(1, max_quorum + 1)
    )

    return GenesisQuorumAnalysis(
        population_size=population_size,
        available_verifiers=available_verifiers,
        rows=rows,
    )
