from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.user_flow import (
    add_relation,
    create_request_context,
    start_user_flow,
)


STAMP = "2026-09-21T00:00:00Z"


def test_start_user_flow_connects_request_to_genesis():
    flow = start_user_flow("request:1", "agent:a", STAMP)

    assert flow.stage == "GENESIS"
    assert flow.context.request_id == "request:1"
    assert flow.context.genesis.subject == "agent:a"
    assert flow.context.relations == ()
    assert flow.context.version == 1
    assert len(flow.id) == 64
    assert len(flow.context.id) == 64


def test_request_context_is_deterministic():
    genesis = create_genesis("agent:a", STAMP)

    first = create_request_context("request:1", STAMP, genesis)
    second = create_request_context("request:1", STAMP, genesis)

    assert first == second
    assert first.id == second.id


def test_add_relation_creates_new_immutable_flow():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    relation = create_relation(flow.context.genesis.id, "agent:b", "trust", STAMP)

    next_flow = add_relation(flow, relation)

    assert flow.stage == "GENESIS"
    assert flow.context.relations == ()
    assert next_flow.stage == "RELATION"
    assert next_flow.context.relations == (relation,)
    assert next_flow.context.participants == frozenset(
        {flow.context.genesis.id, "agent:b"}
    )
    assert next_flow.id != flow.id
    assert next_flow.context.id != flow.context.id


def test_relation_chain_can_extend_existing_context():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    first = create_relation(flow.context.genesis.id, "agent:b", "trust", STAMP)
    flow = add_relation(flow, first)

    second = create_relation("agent:b", "agent:c", "observation", STAMP)
    flow = add_relation(flow, second)

    assert flow.stage == "RELATION"
    assert flow.context.relations == (first, second)
    assert "agent:c" in flow.context.participants


def test_unconnected_relation_is_rejected():
    flow = start_user_flow("request:1", "agent:a", STAMP)
    relation = create_relation("agent:x", "agent:y", "trust", STAMP)

    with pytest.raises(ValueError, match="not connected"):
        add_relation(flow, relation)


def test_invalid_request_context_is_rejected():
    genesis = create_genesis("agent:a", STAMP)

    with pytest.raises(ValueError):
        create_request_context("", STAMP, genesis)

    with pytest.raises(ValueError):
        create_request_context("request:1", "", genesis)

    with pytest.raises(TypeError):
        create_request_context("request:1", STAMP, object())

    with pytest.raises(TypeError):
        create_request_context("request:1", STAMP, genesis, [])


def test_context_and_flow_are_immutable():
    flow = start_user_flow("request:1", "agent:a", STAMP)

    with pytest.raises(FrozenInstanceError):
        flow.stage = "RELATION"

    with pytest.raises(FrozenInstanceError):
        flow.context.request_id = "other"


def test_relation_order_is_part_of_context_identity():
    genesis = create_genesis("agent:a", STAMP)
    first = create_relation(genesis.id, "agent:b", "trust", STAMP)
    second = create_relation("agent:b", "agent:c", "observation", STAMP)

    ordered = create_request_context(
        "request:1", STAMP, genesis, (first, second)
    )
    reversed_order = create_request_context(
        "request:1", STAMP, genesis, (second, first)
    )

    assert ordered.id != reversed_order.id
