"""Canonical evidence graph projection for Agent Ω runtime artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from src.recursive_convergence import RecursiveConvergenceRun


@dataclass(frozen=True)
class EvidenceNode:
    id: str
    type: str
    label: str
    payload_ref: str
    version: int = 1


@dataclass(frozen=True)
class EvidenceEdge:
    source: str
    target: str
    relation: str
    evidence_ref: str
    version: int = 1


@dataclass(frozen=True)
class EvidenceGraph:
    id: str
    nodes: tuple[EvidenceNode, ...]
    edges: tuple[EvidenceEdge, ...]
    version: int = 1

    def as_dict(self) -> dict:
        return asdict(self)


def _node(nodes: dict[str, EvidenceNode], identifier: str, kind: str, label: str) -> None:
    nodes.setdefault(identifier, EvidenceNode(identifier, kind, label, identifier))


def build_evidence_graph(run: RecursiveConvergenceRun) -> EvidenceGraph:
    """Project immutable recursive runtime artifacts into one deterministic graph."""
    if not isinstance(run, RecursiveConvergenceRun):
        raise TypeError("run must be RecursiveConvergenceRun")

    nodes: dict[str, EvidenceNode] = {}
    edges: list[EvidenceEdge] = []

    for cycle in run.cycles:
        result = cycle.result
        proposal = cycle.proposal

        for identifier, kind, label in (
            (proposal.proposer_id, "AGENT", "proposer"),
            (proposal.base_state_id, "STATE", "base state"),
            (proposal.id, "PROPOSAL", f"proposal cycle {cycle.index}"),
            (result.consensus.id, "CONSENSUS", f"consensus cycle {cycle.index}"),
            (result.convergence.id, "CONVERGENCE", f"convergence cycle {cycle.index}"),
            (result.execution.id, "EXECUTION", f"execution cycle {cycle.index}"),
            (result.outcome.id, "OUTCOME", f"outcome cycle {cycle.index}"),
            (result.utility.id, "UTILITY", f"utility cycle {cycle.index}"),
            (result.credit.id, "OMEGA_CREDIT", f"Ω-Credit cycle {cycle.index}"),
            (result.memory.id, "MEMORY", f"memory cycle {cycle.index}"),
            (result.state.id, "STATE", f"next state cycle {cycle.index}"),
        ):
            _node(nodes, identifier, kind, label)

        if cycle.parent_memory_id:
            _node(nodes, cycle.parent_memory_id, "MEMORY", f"parent memory cycle {cycle.index}")
            edges.append(EvidenceEdge(cycle.parent_memory_id, proposal.id, "informs", cycle.parent_memory_id))

        if cycle.parent_outcome_id:
            _node(nodes, cycle.parent_outcome_id, "OUTCOME", f"parent outcome cycle {cycle.index}")
            edges.append(EvidenceEdge(cycle.parent_outcome_id, proposal.id, "informs", cycle.parent_outcome_id))

        for source, target, relation in (
            (proposal.proposer_id, proposal.id, "proposes"),
            (proposal.base_state_id, proposal.id, "targets"),
            (proposal.id, result.consensus.id, "verified_by_consensus"),
            (result.consensus.id, result.convergence.id, "converges"),
            (result.convergence.id, result.execution.id, "authorizes_execution"),
            (result.execution.id, result.outcome.id, "produces"),
            (result.outcome.id, result.utility.id, "measured_as"),
            (result.utility.id, result.credit.id, "credits"),
            (result.outcome.id, result.memory.id, "remembered_as"),
            (result.memory.id, result.state.id, "influences"),
        ):
            edges.append(EvidenceEdge(source, target, relation, result.outcome.id))

        for verification_id in result.consensus.verification_ids:
            _node(nodes, verification_id, "VERIFICATION", f"verification cycle {cycle.index}")
            edges.append(EvidenceEdge(verification_id, result.consensus.id, "supports", verification_id))

    ordered_nodes = tuple(nodes[key] for key in sorted(nodes))
    ordered_edges = tuple(sorted(
        edges, key=lambda item: (item.source, item.target, item.relation, item.evidence_ref)
    ))
    canonical = {
        "nodes": [asdict(item) for item in ordered_nodes],
        "edges": [asdict(item) for item in ordered_edges],
        "version": 1,
    }
    identifier = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return EvidenceGraph(identifier, ordered_nodes, ordered_edges)


__all__ = ["EvidenceNode", "EvidenceEdge", "EvidenceGraph", "build_evidence_graph"]
