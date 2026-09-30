"""Verification of an evolution-history chain against supplied anchors."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.evolution_history_chain import (
    EvolutionHistoryChain,
    create_evolution_history_chain,
)
from src.evolution_history_root_anchor import EvolutionHistoryRootAnchor


@dataclass(frozen=True)
class EvolutionHistoryChainVerification:
    valid: bool
    expected_chain_id: str | None
    provided_chain_id: str | None
    error: str | None
    version: int = 1


def verify_evolution_history_chain(
    anchors: Iterable[EvolutionHistoryRootAnchor],
    chain: EvolutionHistoryChain,
) -> EvolutionHistoryChainVerification:
    if not isinstance(chain, EvolutionHistoryChain):
        raise ValueError("chain must be an EvolutionHistoryChain")

    try:
        expected = create_evolution_history_chain(anchors)
    except (TypeError, ValueError) as exc:
        return EvolutionHistoryChainVerification(
            valid=False,
            expected_chain_id=None,
            provided_chain_id=chain.id,
            error=str(exc),
        )

    valid = expected.id == chain.id
    return EvolutionHistoryChainVerification(
        valid=valid,
        expected_chain_id=expected.id,
        provided_chain_id=chain.id,
        error=None if valid else "chain does not match supplied anchors",
    )
