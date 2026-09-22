"""Canonical Φ structural entry point for theNet."""

from __future__ import annotations

from collections.abc import Iterable

from src.relation import Relation
from src.structure import PhiStructure, create_phi_structure as _create_phi_structure


def create_phi_structure(relations: Iterable[Relation]) -> PhiStructure:
    """Build the canonical immutable Φ topology from Relation objects."""
    return _create_phi_structure(relations)


def create_phi(relations: Iterable[Relation]) -> PhiStructure:
    """Compatibility alias for the canonical Φ constructor."""
    return _create_phi_structure(relations)


__all__ = ["PhiStructure", "create_phi", "create_phi_structure"]
