from dataclasses import FrozenInstanceError

import pytest

from src.omega2 import create_omega_memory


STAMP = "2026-09-21T00:04:00Z"


def test_create_omega_memory():
    memory = create_omega_memory("transition:a", "state:b", STAMP)

    assert memory.transition_id == "transition:a"
    assert memory.state_id == "state:b"
    assert memory.created_at == STAMP
    assert memory.version == 1
    assert len(memory.id) == 64


def test_omega_memory_is_deterministic():
    first = create_omega_memory("transition:a", "state:b", STAMP)
    second = create_omega_memory("transition:a", "state:b", STAMP)

    assert first == second


@pytest.mark.parametrize(
    ("transition_id", "state_id", "created_at"),
    [
        ("", "state:b", STAMP),
        ("transition:a", "", STAMP),
        ("transition:a", "state:b", ""),
    ],
)
def test_empty_fields_are_rejected(transition_id, state_id, created_at):
    with pytest.raises(ValueError):
        create_omega_memory(transition_id, state_id, created_at)


def test_omega_memory_is_immutable():
    memory = create_omega_memory("transition:a", "state:b", STAMP)

    with pytest.raises(FrozenInstanceError):
        memory.state_id = "state:c"


def test_transition_change_changes_identity():
    first = create_omega_memory("transition:a", "state:b", STAMP)
    second = create_omega_memory("transition:b", "state:b", STAMP)

    assert first.id != second.id


def test_state_change_changes_identity():
    first = create_omega_memory("transition:a", "state:b", STAMP)
    second = create_omega_memory("transition:a", "state:c", STAMP)

    assert first.id != second.id
