from dataclasses import FrozenInstanceError

import pytest

from src.agent_state import create_agent_state


BASE = ("agent-1", "iota-1", "2026-09-21T00:00:00Z")


def test_create_agent_state():
    item = create_agent_state(*BASE)

    assert item.subject_id == "agent-1"
    assert item.singularity_id == "iota-1"
    assert item.created_at == BASE[-1]
    assert item.version == 1
    assert len(item.id) == 64


def test_identity_is_deterministic():
    assert create_agent_state(*BASE).id == create_agent_state(*BASE).id


@pytest.mark.parametrize("index", range(3))
def test_empty_input_is_rejected(index):
    values = list(BASE)
    values[index] = "   "

    with pytest.raises(ValueError):
        create_agent_state(*values)


def test_non_string_input_is_rejected():
    values = list(BASE)
    values[1] = None

    with pytest.raises(ValueError):
        create_agent_state(*values)


def test_result_is_immutable():
    item = create_agent_state(*BASE)

    with pytest.raises(FrozenInstanceError):
        item.subject_id = "other"


@pytest.mark.parametrize("index", range(3))
def test_defining_changes_change_identity(index):
    values = list(BASE)
    values[index] += "-changed"

    assert create_agent_state(*values).id != create_agent_state(*BASE).id
