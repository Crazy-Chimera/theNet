from dataclasses import FrozenInstanceError

import pytest

from src.commit import create_evolution_commit


BASE = (
    "state-1",
    "proposal-1",
    "state-1",
    ["verification-b", "verification-a", "verification-a"],
    True,
    "convergence-1",
    True,
    "proposal-1",
    "2026-09-22T00:00:00Z",
)


def test_create_evolution_commit():
    item = create_evolution_commit(*BASE)

    assert item.previous_state_id == "state-1"
    assert item.proposal_id == "proposal-1"
    assert item.verification_ids == ("verification-a", "verification-b")
    assert item.convergence_id == "convergence-1"
    assert item.version == 1
    assert len(item.id) == 64


def test_identity_is_deterministic_and_order_independent():
    left = create_evolution_commit(*BASE)
    values = list(BASE)
    values[3] = ["verification-a", "verification-b"]
    right = create_evolution_commit(*values)

    assert left == right


def test_empty_verifications_are_rejected():
    values = list(BASE)
    values[3] = []

    with pytest.raises(ValueError):
        create_evolution_commit(*values)


@pytest.mark.parametrize("index", [0, 1, 2, 5, 8])
def test_empty_defining_string_is_rejected(index):
    values = list(BASE)
    values[index] = "   "

    with pytest.raises(ValueError):
        create_evolution_commit(*values)


@pytest.mark.parametrize(
    ("index", "value"),
    [(4, 1), (6, 1)],
)
def test_boolean_fields_must_be_boolean(index, value):
    values = list(BASE)
    values[index] = value

    with pytest.raises(ValueError):
        create_evolution_commit(*values)


def test_commit_requires_current_base_state_match():
    values = list(BASE)
    values[2] = "state-2"

    with pytest.raises(ValueError, match="current state"):
        create_evolution_commit(*values)


def test_commit_requires_valid_verifications():
    values = list(BASE)
    values[4] = False

    with pytest.raises(ValueError, match="valid"):
        create_evolution_commit(*values)


def test_commit_requires_convergence():
    values = list(BASE)
    values[6] = False
    values[7] = None

    with pytest.raises(ValueError, match="converged"):
        create_evolution_commit(*values)


def test_commit_requires_matching_resolution():
    values = list(BASE)
    values[7] = "proposal-2"

    with pytest.raises(ValueError, match="different proposal"):
        create_evolution_commit(*values)


def test_result_is_immutable():
    item = create_evolution_commit(*BASE)

    with pytest.raises(FrozenInstanceError):
        item.proposal_id = "other"


def test_defining_changes_change_identity():
    base = create_evolution_commit(*BASE)

    for index in [0, 1, 5, 8]:
        values = list(BASE)
        values[index] = values[index] + "-changed"
        assert create_evolution_commit(*values).id != base.id

    values = list(BASE)
    values[3] = ["verification-c"]
    assert create_evolution_commit(*values).id != base.id
