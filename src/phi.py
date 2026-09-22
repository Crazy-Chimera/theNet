"""Public Φ API backed by the canonical relational topology primitive."""

from __future__ import annotations

from collections.abc import Iterable

from src.relation import Relation
from src.structure import PhiStructure, create_phi_structure


def create_phi(relations: Iterable[Relation]) -> PhiStructure:
    """Create the canonical Φ structure from explicit relations."""
    return create_phi_structure(relations)


__all__ = ["PhiStructure", "create_phi"]
