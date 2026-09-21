from dataclasses import FrozenInstanceError

import pytest

from src.proposal import create_proposal


BASE = (
    "agent-1",
    "state-1",
    "add-relation",
    "2026-09-21T00:00:00Z",
)


def test_create_proposal():
    item = create_proposal(*BASE)

    assert item.proposer_id == "agent-1"
    assert item.base_state_id == "state-1"
    assert item.proposal == "add-relation"
    assert item.version == 1
    assert len(item.id) == 64


def test_identity_is_deterministic():
    assert create_proposal(*BASE).id == create_proposal(*BASE).id


@pytest.mark.parametrize("index", range(4))
def test_empty_input_is_rejected(index):
    values = list(BASE)
    values[index] = "   "

    with pytest.raises(ValueError):
        create_proposal(*values)


def test_non_string_input_is_rejected():
    values = list(BASE)
    values[2] = None

    with pytest.raises(ValueError):
        create_proposal(*values)


def test_result_is_immutable():
    item = create_proposal(*BASE)

    with pytest.raises(FrozenInstanceError):
        item.proposal = "other"


@pytest.mark.parametrize("index", range(4))
def test_defining_changes_change_identity(index):
    values = list(BASE)
    values[index] += "-changed"

    assert create_proposal(*values).id != create_proposal(*BASE).id
