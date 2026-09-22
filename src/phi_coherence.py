"""Deterministic structural coherence derived from Φ."""

from __future__ import annotations

from src.structure import PhiStructure


def phi_coherence(structure: PhiStructure) -> float:
    """Return the structural coherence signal for a Φ structure."""
    if not isinstance(structure, PhiStructure):
        raise TypeError("structure must be PhiStructure")

    if not structure.relation_ids or not structure.node_ids:
        return 0.0

    # PhiStructure stores canonical relation IDs and node IDs, but not relation
    # endpoints. Without endpoints, connectivity cannot be reconstructed.
    # Version 1 therefore treats a non-empty canonical Φ state as coherent by
    # construction. A later schema version can add endpoint data explicitly.
    return 1.0
