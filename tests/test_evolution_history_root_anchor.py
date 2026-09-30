from dataclasses import FrozenInstanceError

import pytest

from src.evolution_history_root_anchor import (
    EvolutionHistoryRootAnchor,
    create_evolution_history_root_anchor,
)


STAMP = "2026-09-30T00:00:00Z"


def test_first_epoch_anchor_is_valid():
    anchor = create_evolution_history_root_anchor("root-1", STAMP)

    assert isinstance(anchor, EvolutionHistoryRootAnchor)
    assert anchor.previous_root_id is None
    assert anchor.current_root_id == "root-1"


def test_chained_anchor_is_valid():
    anchor = create_evolution_history_root_anchor(
        "root-2", STAMP, previous_root_id="root-1"
    )

    assert anchor.previous_root_id == "root-1"
    assert anchor.current_root_id == "root-2"


def test_identity_is_deterministic():
    left = create_evolution_history_root_anchor("root-2", STAMP, "root-1")
    right = create_evolution_history_root_anchor("root-2", STAMP, "root-1")

    assert left == right


@pytest.mark.parametrize(
    "kwargs",
    [
        {"current_root_id": "", "created_at": STAMP},
        {"current_root_id": "root", "created_at": ""},
        {
            "current_root_id": "root",
            "created_at": STAMP,
            "previous_root_id": "",
        },
    ],
)
def test_invalid_identifiers_are_rejected(kwargs):
    with pytest.raises(ValueError):
        create_evolution_history_root_anchor(**kwargs)


def test_root_changes_change_identity():
    assert create_evolution_history_root_anchor(
        "root-2", STAMP, "root-1"
    ).id != create_evolution_history_root_anchor(
        "root-3", STAMP, "root-1"
    ).id


def test_previous_root_changes_change_identity():
    assert create_evolution_history_root_anchor(
        "root-2", STAMP, "root-1"
    ).id != create_evolution_history_root_anchor(
        "root-2", STAMP, "root-0"
    ).id


def test_timestamp_changes_change_identity():
    assert create_evolution_history_root_anchor(
        "root-2", STAMP, "root-1"
    ).id != create_evolution_history_root_anchor(
        "root-2", "2026-09-30T00:01:00Z", "root-1"
    ).id


def test_anchor_is_immutable():
    anchor = create_evolution_history_root_anchor("root-1", STAMP)

    with pytest.raises(FrozenInstanceError):
        anchor.current_root_id = "root-2"


def test_input_values_are_not_mutated():
    previous = "root-1"
    current = "root-2"

    create_evolution_history_root_anchor(current, STAMP, previous)

    assert previous == "root-1"
    assert current == "root-2"
