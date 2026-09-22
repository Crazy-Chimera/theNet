"""Deterministic structural coherence derived from Φ."""

from __future__ import annotations

from src.structure import PhiStructure


def phi_coherence(structure: PhiStructure) -> float:
    """Return largest weakly connected component coverage."""
    if not isinstance(structure, PhiStructure):
        raise TypeError("structure must be PhiStructure")

    nodes = set(structure.node_ids)
    if not nodes:
        return 0.0

    adjacency = {node: set() for node in nodes}
    for source, target in structure.edges:
        adjacency[source].add(target)
        adjacency[target].add(source)

    largest = 0
    remaining = set(nodes)

    while remaining:
        root = remaining.pop()
        component = {root}
        stack = [root]

        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)

        largest = max(largest, len(component))

    return largest / len(nodes)
