from dataclasses import FrozenInstanceError

import pytest

from src.verification import create_verification


BASE = (
    "proposal-1",
    "verifier-1",
    "evidence-hash",
    True,
    "2026-09-21T00:00:00Z",
)


def test_create_verification():
    item = create_verification(*BASE)

    assert item.proposal_id == "proposal-1"
    assert item.verifier_id == "verifier-1"
    assert item.evidence == "evidence-hash"
    assert item.valid is True
    assert item.version == 1
    assert len(item.id) == 64


def test_identity_is_deterministic():
    assert create_verification(*BASE).id == create_verification(*BASE).id


@pytest.mark.parametrize("index", [0, 1, 2, 4])
def test_empty_input_is_rejected(index):
    values = list(BASE)
    values[index] = "   "

    with pytest.raises(ValueError):
        create_verification(*values)


def test_valid_must_be_boolean():
    values = list(BASE)
    values[3] = 1

    with pytest.raises(ValueError):
        create_verification(*values)


@pytest.mark.parametrize("index", range(5))
def test_defining_changes_change_identity(index):
    values = list(BASE)
    if index == 3:
        values[index] = False
    else:
        values[index] += "-changed"

    assert create_verification(*values).id != create_verification(*BASE).id


def test_result_is_immutable():
    item = create_verification(*BASE)

    with pytest.raises(FrozenInstanceError):
        item.valid = False
