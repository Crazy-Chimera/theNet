from __future__ import annotations

from thenet.engine import (
    advance_collectively,
    commit_self_organizing_resources_from_phi,
)
from src.agent_state import create_agent_state
from src.genesis import create_genesis
from src.memory import create_memory
from src.phi import create_phi
from src.proposal import create_proposal
from src.relation import create_relation
from src.resource_state import create_resource_state
from src.verification import create_verification


STAMP = "2026-09-22T16:00:00Z"


def test_verified_evolution_can_feed_self_organizing_resource_flow():
    agent = create_genesis("agent-a", STAMP)
    verifier = create_genesis("agent-b", STAMP)
    state = create_agent_state(agent.id, "singularity-a", STAMP)

    proposal = create_proposal(
        agent.id,
        state.id,
        "verified relational learning",
        STAMP,
    )
    verification = create_verification(
        proposal.id,
        verifier.id,
        "evidence-b",
        True,
        STAMP,
    )

    evolution = advance_collectively(
        state,
        proposal,
        [verification],
        quorum=1,
        new_singularity_id="singularity-b",
        created_at=STAMP,
    )

    assert evolution.consensus.reached is True
    assert evolution.commit.previous_state_id == state.id
    assert evolution.state.id != state.id
    assert evolution.state.version == state.version + 1

    relation = create_relation(agent.id, verifier.id, "supports", STAMP)
    phi = create_phi([relation])

    memory = create_memory(
        agent.id,
        evolution.commit.id,
        "verified-learning",
        STAMP,
    )
    assert memory.source_id == evolution.commit.id

    memory_resource = create_resource_state(100.0, 0.0, STAMP)
    compute_resource = create_resource_state(100.0, 0.0, STAMP)

    next_memory, next_compute = commit_self_organizing_resources_from_phi(
        [
            _relational_utility(
                contributor_id=agent.id,
                evidence_id=memory.id,
            )
        ],
        memory_resource,
        compute_resource,
        {agent.id: phi},
        "2026-09-22T16:01:00Z",
    )

    assert next_memory.used > 0.0
    assert next_compute.used > 0.0
    assert next_memory.used <= next_memory.available
    assert next_compute.used <= next_compute.available


def _relational_utility(contributor_id: str, evidence_id: str):
    from src.relational_utility import create_relational_utility

    return create_relational_utility(
        contributor_id,
        1.0,
        [evidence_id],
        True,
        STAMP,
    )
