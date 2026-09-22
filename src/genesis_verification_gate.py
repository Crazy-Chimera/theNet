"""Minimal deterministic gate for first Genesis collective verification."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenesisVerificationGate:
    population_size: int
    verifier_count: int
    required_quorum: int
    approved: bool
    reputation_required: bool = False
    version: int = 1


def evaluate_genesis_verification(
    population_size: int,
    verifier_count: int,
    required_quorum: int = 1,
) -> GenesisVerificationGate:
    if (
        not isinstance(population_size, int)
        or isinstance(population_size, bool)
        or population_size < 1
    ):
        raise ValueError("population_size must be a positive integer")

    if (
        not isinstance(verifier_count, int)
        or isinstance(verifier_count, bool)
        or verifier_count < 0
    ):
        raise ValueError("verifier_count must be a non-negative integer")

    if (
        not isinstance(required_quorum, int)
        or isinstance(required_quorum, bool)
        or required_quorum < 1
    ):
        raise ValueError("required_quorum must be a positive integer")

    max_verifiers = population_size - 1
    if verifier_count > max_verifiers:
        raise ValueError("verifier_count cannot exceed independent population")

    return GenesisVerificationGate(
        population_size=population_size,
        verifier_count=verifier_count,
        required_quorum=required_quorum,
        approved=verifier_count >= required_quorum,
    )
