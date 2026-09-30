"""Deterministic query operations over the canonical Evidence Graph."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass

from src.evidence_graph import EvidenceEdge, EvidenceGraph, EvidenceNode


@dataclass(frozen=True)
class EvidenceQueryResult:
    node_id: str
    direction: str
    nodes: tuple[EvidenceNode, ...]
    edges: tuple[EvidenceEdge, ...]
    depth: int
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


def _adjacent(graph: EvidenceGraph, node_id: str, direction: str) -> tuple[EvidenceEdge, ...]:
    if direction == "forward":
        return tuple(edge for edge in graph.edges if edge.source == node_id)
    if direction == "backward":
        return tuple(edge for edge in graph.edges if edge.target == node_id)
    if direction == "both":
        return tuple(
            edge for edge in graph.edges
            if edge.source == node_id or edge.target == node_id
        )
    raise ValueError("direction must be forward, backward, or both")


def query_evidence_graph(
    graph: EvidenceGraph,
    node_id: str,
    *,
    direction: str = "both",
    max_depth: int = 1,
    relation: str | None = None,
    node_type: str | None = None,
) -> EvidenceQueryResult:
    """Return a deterministic bounded traversal without mutating the graph."""
    if not isinstance(graph, EvidenceGraph):
        raise TypeError("graph must be EvidenceGraph")
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("node_id must be non-empty")
    if not isinstance(max_depth, int) or max_depth < 0:
        raise ValueError("max_depth must be a non-negative integer")
    if node_id not in {node.id for node in graph.nodes}:
        raise KeyError(f"unknown node_id: {node_id}")

    node_by_id = {node.id: node for node in graph.nodes}
    visited = {node_id}
    distances = {node_id: 0}
    queue = deque([node_id])
    selected_edges: set[tuple[str, str, str, str]] = set()

    while queue:
        current = queue.popleft()
        depth = distances[current]
        if depth >= max_depth:
            continue
        for edge in sorted(_adjacent(graph, current, direction),
                           key=lambda item: (item.source, item.target, item.relation, item.evidence_ref)):
            if relation is not None and edge.relation != relation:
                continue
            if direction == "forward":
                other = edge.target
            elif direction == "backward":
                other = edge.source
            else:
                other = edge.target if edge.source == current else edge.source
            selected_edges.add((edge.source, edge.target, edge.relation, edge.evidence_ref))
            if other not in visited:
                visited.add(other)
                distances[other] = depth + 1
                queue.append(other)

    selected_nodes = tuple(
        node_by_id[item]
        for item in sorted(visited)
        if node_type is None or node_by_id[item].type == node_type
    )
    selected_node_ids = {node.id for node in selected_nodes}
    selected = tuple(
        edge for edge in graph.edges
        if (edge.source, edge.target, edge.relation, edge.evidence_ref) in selected_edges
        and edge.source in selected_node_ids
        and edge.target in selected_node_ids
    )
    return EvidenceQueryResult(
        node_id=node_id,
        direction=direction,
        nodes=selected_nodes,
        edges=tuple(sorted(selected, key=lambda item: (item.source, item.target, item.relation, item.evidence_ref))),
        depth=max(distances.values(), default=0),
    )


def trace_evidence_path(
    graph: EvidenceGraph,
    source_id: str,
    target_id: str,
    *,
    direction: str = "both",
    max_depth: int = 16,
) -> EvidenceQueryResult:
    """Return the first deterministic bounded path between two graph nodes."""
    if source_id == target_id:
        node = next((item for item in graph.nodes if item.id == source_id), None)
        if node is None:
            raise KeyError(f"unknown node_id: {source_id}")
        return EvidenceQueryResult(source_id, direction, (node,), (), 0)

    node_ids = {node.id for node in graph.nodes}
    if source_id not in node_ids or target_id not in node_ids:
        raise KeyError("source_id and target_id must exist")

    queue = deque([source_id])
    parent: dict[str, tuple[str, EvidenceEdge]] = {}
    visited = {source_id}

    while queue and len(parent) <= max_depth:
        current = queue.popleft()
        for edge in sorted(_adjacent(graph, current, direction),
                           key=lambda item: (item.source, item.target, item.relation, item.evidence_ref)):
            other = edge.target if direction == "forward" else edge.source if direction == "backward" else (
                edge.target if edge.source == current else edge.source
            )
            if other in visited:
                continue
            visited.add(other)
            parent[other] = (current, edge)
            if other == target_id:
                queue.clear()
                break
            queue.append(other)

    if target_id not in parent:
        return EvidenceQueryResult(source_id, direction, (), (), -1)

    path_edges: list[EvidenceEdge] = []
    current = target_id
    while current != source_id:
        previous, edge = parent[current]
        path_edges.append(edge)
        current = previous
    path_edges.reverse()
    path_ids = {source_id, target_id}
    for edge in path_edges:
        path_ids.add(edge.source)
        path_ids.add(edge.target)
    nodes = tuple(node for node in graph.nodes if node.id in path_ids)
    return EvidenceQueryResult(
        node_id=source_id,
        direction=direction,
        nodes=nodes,
        edges=tuple(path_edges),
        depth=len(path_edges),
    )


__all__ = ["EvidenceQueryResult", "query_evidence_graph", "trace_evidence_path"]
