import pytest

from src.genesis import create_genesis
from src.omega_credit import OmegaCredit
from src.phi_omega_credit import create_omega_credit_from_phi
from src.phi import create_phi
from src.relational_utility import create_relational_utility
from src.relation import create_relation


STAMP = "2026-09-22T00:00:00Z"


def test_phi_credit_derives_full_coherence():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    relation = create_relation(a.id, b.id, "supports", STAMP)
    utility = create_relational_utility("a", 0.8, ("evidence-1",), True, STAMP)

    credit = create_omega_credit_from_phi(
        utility, 0.5, create_phi([relation]), STAMP
    )

    assert isinstance(credit, OmegaCredit)
    assert credit.coherence == 1.0
    assert credit.credit == pytest.approx(0.4)


def test_phi_credit_is_zero_for_unverified_utility():
    relation = create_relation("a", "b", "supports", STAMP)
    utility = create_relational_utility("a", 0.8, (), False, STAMP)

    credit = create_omega_credit_from_phi(
        utility, 0.5, create_phi([relation]), STAMP
    )

    assert credit.credit == 0.0
    assert credit.verified is False


def test_phi_credit_reflects_disconnected_coherence():
    first = create_relation("a", "b", "supports", STAMP)
    second = create_relation("c", "d", "supports", STAMP)
    utility = create_relational_utility("a", 1.0, ("evidence-1",), True, STAMP)

    credit = create_omega_credit_from_phi(
        utility, 1.0, create_phi([first, second]), STAMP
    )

    assert credit.coherence == pytest.approx(0.5)
    assert credit.credit == pytest.approx(0.5)


def test_phi_credit_rejects_wrong_types():
    utility = create_relational_utility("a", 1.0, ("evidence-1",), True, STAMP)
    with pytest.raises(TypeError):
        create_omega_credit_from_phi(utility, 1.0, object(), STAMP)
