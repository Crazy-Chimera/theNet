"""Deterministic immutable chain of evolution-history root anchors."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json

from src.evolution_history_root_anchor import EvolutionHistoryRootAnchor


@dataclass(frozen=True)
class EvolutionHistoryChain:
    id: str
    anchor_ids: tuple[str, ...]
    root_ids: tuple[str, ...]
    version: int = 1

    @property
    def length(self) -> int:
        return len(self.anchor_ids)


def _canonical(anchor_ids: tuple[str, ...], root_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "anchor_ids": anchor_ids,
            "root_ids": root_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def create_evolution_history_chain(
    anchors: Iterable[EvolutionHistoryRootAnchor],
) -> EvolutionHistoryChain:
    items = tuple(anchors)

    if not items:
        raise ValueError("anchors must contain at least one anchor")

    if any(not isinstance(anchor, EvolutionHistoryRootAnchor) for anchor in items):
        raise TypeError("anchors must contain only EvolutionHistoryRootAnchor objects")

    if items[0].previous_root_id is not None:
        raise ValueError("first anchor must not have a previous_root_id")

    for previous, current in zip(items, items[1:]):
        if current.previous_root_id != previous.current_root_id:
            raise ValueError("anchors do not form a continuous root chain")

    anchor_ids = tuple(anchor.id for anchor in items)
    root_ids = tuple(anchor.current_root_id for anchor in items)

    identifier = sha256(
        _canonical(anchor_ids, root_ids).encode("utf-8")
    ).hexdigest()

    return EvolutionHistoryChain(
        id=identifier,
        anchor_ids=anchor_ids,
        root_ids=root_ids,
    )


def create_history_chain(
    anchors: Iterable[EvolutionHistoryRootAnchor],
) -> EvolutionHistoryChain:
    return create_evolution_history_chain(anchors)
