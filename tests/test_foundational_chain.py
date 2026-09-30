"""End-to-end specification for the foundational Genesis → Relation → State → Observe → Φ chain."""

from src.genesis import create_genesis
from src.phi import create_phi_from_observation
from src.relation import create_relation
from src.state import create_state, observe
from src.user_flow import add_relation, start_user_flow


STAMP = "2026-09-30T00:00:00Z"


def test_foundational_chain_is_composable_and_deterministic():
    flow = start_user_flow("request:foundation", "agent:a", STAMP)
    genesis = flow.context.genesis

    relation = create_relation(
        source_id=genesis.id,
        target_id="agent:b",
        kind="supports",
        created_at=STAMP,
    )
    related_flow = add_relation(flow, relation)

    state = create_state(related_flow)
    observation = observe(state)
    phi = create_phi_from_observation(observation, [relation])

    assert genesis.subject == "agent:a"
    assert related_flow.stage == "RELATION"
    assert state.relation_ids == (relation.id,)
    assert observation.relation_ids == (relation.id,)
    assert phi.relation_ids == (relation.id,)
    assert phi.node_ids == tuple(sorted((genesis.id, "agent:b")))
    assert phi.edges == ((genesis.id, "agent:b"),)


def test_foundational_chain_changes_structurally_when_relation_changes():
    flow = start_user_flow("request:foundation", "agent:a", STAMP)
    first = create_relation(flow.context.genesis.id, "agent:b", "supports", STAMP)
    second = create_relation(flow.context.genesis.id, "agent:c", "supports", STAMP)

    first_phi = create_phi_from_observation(
        observe(create_state(add_relation(flow, first))),
        [first],
    )
    second_phi = create_phi_from_observation(
        observe(create_state(add_relation(flow, second))),
        [second],
    )

    assert first_phi.id != second_phi.id
    assert first_phi.edges != second_phi.edges


def test_foundational_chain_preserves_relation_direction():
    flow = start_user_flow("request:foundation", "agent:a", STAMP)
    forward = create_relation(flow.context.genesis.id, "agent:b", "supports", STAMP)
    reverse = create_relation("agent:b", flow.context.genesis.id, "supports", STAMP)

    forward_phi = create_phi_from_observation(
        observe(create_state(add_relation(flow, forward))),
        [forward],
    )
    reverse_phi = create_phi_from_observation(
        observe(create_state(add_relation(flow, reverse))),
        [reverse],
    )

    assert forward_phi.id != reverse_phi.id
    assert forward_phi.edges == ((flow.context.genesis.id, "agent:b"),)
    assert reverse_phi.edges == (("agent:b", flow.context.genesis.id),)
