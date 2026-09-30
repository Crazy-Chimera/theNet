from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.state import create_state, observe
from src.user_flow import add_relation, start_user_flow


STAMP = "2026-09-30T00:00:00Z"


def test_user_flow_to_state():
    flow = start_user_flow("request:1", "agent:a", STAMP)

    state = create_state(flow)

    assert state.flow_id == flow.id
    assert state.context_id == flow.context.id
    assert state.subject_id == "agent:a"
    assert state.stage == "GENESIS"
    assert state.relation_ids == ()


def test_relation_flow_produces_new_state():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    relation = create_relation(flow.context.genesis.id, "agent:b", "trust", STAMP)

    next_flow = add_relation(flow, relation)
    first = create_state(flow)
    second = create_state(next_flow)

    assert first.id != second.id
    assert second.stage == "RELATION"
    assert second.relation_ids == (relation.id,)


def test_state_is_deterministic():
    flow = start_user_flow("request:1", "agent:a", STAMP)

    assert create_state(flow) == create_state(flow)


def test_state_is_immutable():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    state = create_state(flow)

    with pytest.raises(FrozenInstanceError):
        state.stage = "OTHER"


def test_create_state_requires_user_flow():
    with pytest.raises(TypeError):
        create_state("flow:1")


def test_observe_is_pure_and_deterministic():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    state = create_state(flow)

    first = observe(state)
    second = observe(state)

    assert first == second
    assert first.state_id == state.id
    assert first.subject_id == "agent:a"
    assert first.stage == "GENESIS"
    assert first.relation_count == 0


def test_observe_relation_state():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    relation = create_relation(flow.context.genesis.id, "agent:b", "trust", STAMP)
    flow = add_relation(flow, relation)

    observation = observe(create_state(flow))

    assert observation.stage == "RELATION"
    assert observation.relation_count == 1
    assert observation.relation_ids == (relation.id,)


def test_observe_requires_state():
    with pytest.raises(TypeError):
        observe(None)
