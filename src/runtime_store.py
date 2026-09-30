"""Backend-neutral persistence contract for theNet."""

from __future__ import annotations

from typing import Protocol

from src.genesis import GenesisState
from src.relation import Relation


class RuntimeStore(Protocol):
    """Persistence boundary for immutable theNet domain objects."""

    def save_genesis(self, state: GenesisState) -> None:
        ...

    def get_genesis(self, state_id: str) -> GenesisState | None:
        ...

    def save_relation(self, relation: Relation) -> None:
        ...

    def get_relation(self, relation_id: str) -> Relation | None:
        ...

    def close(self) -> None:
        ...