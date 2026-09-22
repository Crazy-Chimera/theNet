"""Compatibility entry point for the canonical Φ relational topology."""

from __future__ import annotations

from collections.abc import Iterable

from src.relation import Relation
from src.structure import PhiStructure, create_phi_structure as _create_phi_structure


def create_phi_structure(relations: Iterable[Relation]) -> PhiStructure:
    """Delegate Φ construction to the canonical relational topology."""
    return _create_phi_structure(relations)


__all__ = ["PhiStructure", "create_phi_structure"]
