import pytest

from src.genesis import create_genesis
from src.omega_credit import OmegaCredit
from src.omega_credit_state import create_omega_credit_from_state
from src.phi import create_phi_structure
from src.relational_utility import create_relational_utility
from src.resource_state import create_resource_state
from src.relation import create_relation


STAMP = "2026-09-22T00:00:00Z"


def make_structure():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    relation = create_relation(a.id, b.id, "supports", STAMP)
    return create_phi_structure([relation])


def make_utility(verified=True):
    return create_relational_utility(
        contributor_id="agent-a",
        value=0.8,
        evidence_ids=["e1"],
        verified=verified,
        created_at=STAMP,
    )


def test_state_derived_credit_composes_canonical_signals():
    credit = create_omega_credit_from_state(
        utility=make_utility(),
        resource=create_resource_state(available=10, used=2, created_at=STAMP),
        structure=make_structure(),
        created_at=STAMP,
    )

    assert isinstance(credit, OmegaCredit)
    assert credit.relational_utility == 0.8
    assert credit.resource_efficiency == 0.8
    assert credit.coherence == 1.0
    assert credit.verified is True
    assert credit.credit == pytest.approx(0.64)


def test_exhausted_resource_produces_zero_credit():
    credit = create_omega_credit_from_state(
        utility=make_utility(),
        resource=create_resource_state(available=10, used=10, created_at=STAMP),
        structure=make_structure(),
        created_at=STAMP,
    )

    assert credit.resource_efficiency == 0.0
    assert credit.credit == 0.0


def test_oversubscribed_resource_is_clamped_to_zero_headroom():
    credit = create_omega_credit_from_state(
        utility=make_utility(),
        resource=create_resource_state(available=10, used=12, created_at=STAMP),
        structure=make_structure(),
        created_at=STAMP,
    )

    assert credit.resource_efficiency == 0.0
    assert credit.credit == 0.0


def test_zero_capacity_produces_zero_resource_signal():
    credit = create_omega_credit_from_state(
        utility=make_utility(),
        resource=create_resource_state(available=0, used=0, created_at=STAMP),
        structure=make_structure(),
        created_at=STAMP,
    )

    assert credit.resource_efficiency == 0.0
    assert credit.credit == 0.0


def test_unverified_utility_remains_uncredited():
    credit = create_omega_credit_from_state(
        utility=make_utility(verified=False),
        resource=create_resource_state(available=10, used=2, created_at=STAMP),
        structure=make_structure(),
        created_at=STAMP,
    )

    assert credit.verified is False
    assert credit.credit == 0.0


@pytest.mark.parametrize("argument", ["utility", "resource", "structure"])
def test_domain_boundaries_reject_wrong_types(argument):
    values = {
        "utility": make_utility(),
        "resource": create_resource_state(10, 2, STAMP),
        "structure": make_structure(),
    }
    values[argument] = object()

    with pytest.raises(TypeError):
        create_omega_credit_from_state(
            utility=values["utility"],
            resource=values["resource"],
            structure=values["structure"],
            created_at=STAMP,
        )


def test_same_state_is_deterministic():
    kwargs = {
        "utility": make_utility(),
        "resource": create_resource_state(10, 2, STAMP),
        "structure": make_structure(),
        "created_at": STAMP,
    }

    assert create_omega_credit_from_state(**kwargs) == create_omega_credit_from_state(**kwargs)
