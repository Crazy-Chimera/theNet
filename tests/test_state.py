from dataclasses import FrozenInstanceError

import pytest

from src.state import create_state, observe


def test_create_empty_state():
    state = create_state("flow:1", "agent:a")

    assert state.flow_id == "flow:1"
    assert state.subject_id == "agent:a"
    assert state.events == ()
    assert state.version == 1
    assert len(state.id) == 64


def test_state_is_deterministic():
    events = ("event:1", "event:2")

    assert create_state("flow:1", "agent:a", events) == create_state(
        "flow:1", "agent:a", events
    )


def test_event_order_is_part_of_state_identity():
    first = create_state("flow:1", "agent:a", ("event:1", "event:2"))
    second = create_state("flow:1", "agent:a", ("event:2", "event:1"))

    assert first.id != second.id


@pytest.mark.parametrize(
    ("flow_id", "subject_id"),
    [("", "agent:a"), ("flow:1", "")],
)
def test_required_text_is_validated(flow_id, subject_id):
    with pytest.raises(ValueError):
        create_state(flow_id, subject_id)


def test_events_are_validated():
    with pytest.raises(TypeError):
        create_state("flow:1", "agent:a", ["event:1"])

    with pytest.raises(ValueError):
        create_state("flow:1", "agent:a", ("event:1", ""))


def test_state_is_immutable():
    state = create_state("flow:1", "agent:a")

    with pytest.raises(FrozenInstanceError):
        state.flow_id = "flow:2"


def test_observe_is_pure_and_deterministic():
    state = create_state("flow:1", "agent:a", ("event:1", "event:2"))

    first = observe(state)
    second = observe(state)

    assert first == second
    assert first.state_id == state.id
    assert first.event_count == 2
    assert first.events == state.events


def test_observe_does_not_change_state():
    state = create_state("flow:1", "agent:a", ("event:1",))

    before = state
    observe(state)

    assert state == before
