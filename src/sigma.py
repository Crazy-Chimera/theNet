"""Canonical Σ essence entry point for theNet."""

from __future__ import annotations

from collections.abc import Iterable

from src.essence import Essence, create_essence as _create_essence


def create_essence(relation_ids: Iterable[str]) -> Essence:
    """Build the canonical immutable Σ ground from relation identifiers."""
    return _create_essence(tuple(relation_ids))


__all__ = ["Essence", "create_essence"]
