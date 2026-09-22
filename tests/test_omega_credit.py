from dataclasses import FrozenInstanceError

import pytest

from src.omega_credit import create_omega_credit, create_omega_credit_from_utility
from src.relational_utility import create_relational_utility


BASE = (
    "agent-a",
    0.8,
    0.5,
    0.9,
    True,
    "2026-09-22T06:00:00Z",
)


def test_verified_credit_is_multiplicative():
    item = create_omega_credit(*BASE)

    assert item.credit == pytest.approx(0.8 * 0.5 * 0.9)
    assert 0.0 <= item.credit <= 1.0


def test_unverified_evidence_receives_zero_credit():
    values = list(BASE)
    values[4] = False

    item = create_omega_credit(*values)

    assert item.credit == 0.0


def test_credit_is_deterministic():
    assert create_omega_credit(*BASE) == create_omega_credit(*BASE)


@pytest.mark.parametrize("index", [0, 1, 2, 3, 4, 5])
def test_defining_input_changes_identity(index):
    base = create_omega_credit(*BASE)
    values = list(BASE)

    if index == 0:
        values[index] = "agent-b"
    elif index == 1:
        values[index] = 0.7
    elif index == 2:
        values[index] = 0.4
    elif index == 3:
        values[index] = 0.8
    elif index == 4:
        values[index] = False
    else:
        values[index] = "2026-09-22T06:01:00Z"

    assert create_omega_credit(*values).id != base.id


def test_unit_inputs_are_valid_at_boundaries():
    item = create_omega_credit("agent-a", 0, 1, 0, True, "now")

    assert item.credit == 0.0


@pytest.mark.parametrize("index", [1, 2, 3])
def test_unit_inputs_reject_out_of_range_values(index):
    values = list(BASE)
    values[index] = 1.1

    with pytest.raises(ValueError):
        create_omega_credit(*values)


@pytest.mark.parametrize("index", [1, 2, 3])
def test_unit_inputs_reject_non_finite_values(index):
    values = list(BASE)
    values[index] = float("nan")

    with pytest.raises(ValueError):
        create_omega_credit(*values)


def test_rejects_non_boolean_verified():
    values = list(BASE)
    values[4] = 1

    with pytest.raises(ValueError):
        create_omega_credit(*values)


def test_rejects_empty_identity_fields():
    for index in [0, 5]:
        values = list(BASE)
        values[index] = ""

        with pytest.raises(ValueError):
            create_omega_credit(*values)


def test_result_is_immutable():
    item = create_omega_credit(*BASE)

    with pytest.raises(FrozenInstanceError):
        item.credit = 0.0


def test_verified_utility_flows_into_credit_without_replacing_verification():
    utility = create_relational_utility(
        "agent-a",
        0.8,
        ["evidence-a"],
        True,
        "2026-09-22T06:00:00Z",
    )

    item = create_omega_credit_from_utility(
        utility,
        resource_efficiency=0.5,
        coherence=0.9,
        created_at="2026-09-22T06:01:00Z",
    )

    assert item.contributor_id == utility.contributor_id
    assert item.relational_utility == utility.value
    assert item.verified is True
    assert item.credit == pytest.approx(0.8 * 0.5 * 0.9)


def test_unverified_utility_cannot_receive_credit():
    utility = create_relational_utility(
        "agent-a",
        1.0,
        [],
        False,
        "2026-09-22T06:00:00Z",
    )

    item = create_omega_credit_from_utility(
        utility,
        resource_efficiency=1.0,
        coherence=1.0,
        created_at="2026-09-22T06:01:00Z",
    )

    assert item.verified is False
    assert item.credit == 0.0


def test_utility_adapter_requires_relational_utility():
    with pytest.raises(TypeError):
        create_omega_credit_from_utility(
            object(),
            resource_efficiency=1.0,
            coherence=1.0,
            created_at="2026-09-22T06:01:00Z",
        )
