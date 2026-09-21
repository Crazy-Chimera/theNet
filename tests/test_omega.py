from dataclasses import FrozenInstanceError

import pytest

from src.omega import create_omega_transition


STAMP = "2026-09-21T00:03:00Z"


def test_create_omega_transition():
    transition = create_omega_transition(
        "state:a",
        "state:b",
        "verified evolution",
        STAMP,
    )

    assert transition.from_state == "state:a"
    assert transition.to_state == "state:b"
    assert transition.reason == "verified evolution"
    assert transition.created_at == STAMP
    assert transition.version == 1
    assert len(transition.id) == 64


def test_omega_transition_is_deterministic():
    first = create_omega_transition("state:a", "state:b", "evolve", STAMP)
    second = create_omega_transition("state:a", "state:b", "evolve", STAMP)

    assert first == second


@pytest.mark.parametrize(
    ("from_state", "to_state", "reason", "created_at"),
    [
        ("", "state:b", "evolve", STAMP),
        ("state:a", "", "evolve", STAMP),
        ("state:a", "state:b", "", STAMP),
        ("state:a", "state:b", "evolve", ""),
    ],
)
def test_empty_fields_are_rejected(from_state, to_state, reason, created_at):
    with pytest.raises(ValueError):
        create_omega_transition(from_state, to_state, reason, created_at)


def test_omega_transition_is_immutable():
    transition = create_omega_transition("state:a", "state:b", "evolve", STAMP)

    with pytest.raises(FrozenInstanceError):
        transition.reason = "other"


def test_state_change_changes_identity():
    first = create_omega_transition("state:a", "state:b", "evolve", STAMP)
    second = create_omega_transition("state:a", "state:c", "evolve", STAMP)

    assert first.id != second.id


def test_reason_changes_identity():
    first = create_omega_transition("state:a", "state:b", "evolve", STAMP)
    second = create_omega_transition("state:a", "state:b", "repair", STAMP)

    assert first.id != second.id


def test_self_transition_is_structurally_valid():
    transition = create_omega_transition(
        "state:a",
        "state:a",
        "re-evaluate",
        STAMP,
    )

    assert transition.from_state == transition.to_state
    assert len(transition.id) == 64
