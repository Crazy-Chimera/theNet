from dataclasses import FrozenInstanceError

import pytest

from src.genesis import create_genesis


def test_create_genesis():
    state = create_genesis("agent:genesis", "2026-09-21T00:00:00Z")

    assert state.subject == "agent:genesis"
    assert state.created_at == "2026-09-21T00:00:00Z"
    assert state.relations == ()
    assert state.version == 1
    assert len(state.id) == 64


def test_genesis_is_deterministic():
    first = create_genesis("agent:genesis", "2026-09-21T00:00:00Z")
    second = create_genesis("agent:genesis", "2026-09-21T00:00:00Z")

    assert first == second


@pytest.mark.parametrize("subject", ["", "   "])
def test_empty_subject_is_rejected(subject):
    with pytest.raises(ValueError):
        create_genesis(subject, "2026-09-21T00:00:00Z")


@pytest.mark.parametrize("created_at", ["", "   "])
def test_empty_timestamp_is_rejected(created_at):
    with pytest.raises(ValueError):
        create_genesis("agent:genesis", created_at)


def test_output_is_immutable():
    state = create_genesis("agent:genesis", "2026-09-21T00:00:00Z")

    with pytest.raises(FrozenInstanceError):
        state.subject = "changed"


def test_initial_relations_are_empty():
    state = create_genesis("agent:genesis", "2026-09-21T00:00:00Z")

    assert state.relations == ()
