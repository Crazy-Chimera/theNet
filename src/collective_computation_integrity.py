"""Pure integrity audit for a completed Agent Ω collective computation cycle."""

from __future__ import annotations

from src.collective_computation import CollectiveComputationCycle
from src.resource_state import ResourceState


def verify_collective_computation_integrity(
    cycle: CollectiveComputationCycle,
) -> bool:
    """Validate cross-layer references without mutating or repairing the cycle."""
    if not isinstance(cycle, CollectiveComputationCycle):
        return False

    evolution = cycle.evolution
    consensus = evolution.consensus
    commit = evolution.commit
    memory = cycle.memory
    utility = cycle.utility

    if not consensus.reached:
        return False
    if tuple(commit.verification_ids) != tuple(consensus.verification_ids):
        return False
    if memory.source_id != commit.id:
        return False
    if not utility.verified or memory.id not in utility.evidence_ids:
        return False
    if utility.contributor_id != evolution.state.subject_id:
        return False

    verifier_ids = tuple(sorted(relation.target_id for relation in cycle.relations))
    if verifier_ids != tuple(consensus.verifier_ids):
        return False

    relation_ids = tuple(sorted(relation.id for relation in cycle.relations))
    if relation_ids != tuple(cycle.phi.relation_ids):
        return False

    expected_edges = tuple(
        (relation.source_id, relation.target_id)
        for relation in sorted(cycle.relations, key=lambda item: item.id)
    )
    if expected_edges != tuple(cycle.phi.edges):
        return False

    if not isinstance(cycle.memory_resource, ResourceState):
        return False
    if not isinstance(cycle.compute_resource, ResourceState):
        return False

    return True


__all__ = ["verify_collective_computation_integrity"]
