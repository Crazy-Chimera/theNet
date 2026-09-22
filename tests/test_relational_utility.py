from dataclasses import FrozenInstanceError

import pytest

from src.relational_utility import create_relational_utility


STAMP = "2026-09-22T00:00:00Z"


def test_creates_verified_relational_utility():
    utility = create_relational_utility(
        "agent:a",
        0.8,
        ["evidence:b", "evidence:a", "evidence:a"],
        True,
        STAMP,
    )

    assert utility.contributor_id == "agent:a"
    assert utility.value == 0.8
    assert utility.evidence_ids == ("evidence:a", "evidence:b")
    assert utility.verified is True
    assert len(utility.id) == 64


def test_unverified_utility_can_exist_without_evidence():
    utility = create_relational_utility("agent:a", 0.8, [], False, STAMP)

    assert utility.verified is False
    assert utility.evidence_ids == ()


def test_verified_utility_requires_evidence():
    with pytest.raises(ValueError):
        create_relational_utility("agent:a", 0.8, [], True, STAMP)


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf")])
def test_value_must_be_bounded_and_finite(value):
    with pytest.raises(ValueError):
        create_relational_utility("agent:a", value, ["e"], True, STAMP)


def test_utility_identity_is_deterministic():
    left = create_relational_utility("agent:a", 0.8, ["e"], True, STAMP)
    right = create_relational_utility("agent:a", 0.8, ["e"], True, STAMP)

    assert left == right


def test_utility_changes_identity_when_defining_input_changes():
    base = create_relational_utility("agent:a", 0.8, ["e"], True, STAMP)
    changed = create_relational_utility("agent:a", 0.9, ["e"], True, STAMP)

    assert base.id != changed.id


def test_utility_is_immutable():
    utility = create_relational_utility("agent:a", 0.8, ["e"], True, STAMP)

    with pytest.raises(FrozenInstanceError):
        utility.value = 0.9
