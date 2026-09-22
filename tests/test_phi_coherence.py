import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.structure import create_phi_structure
from src.phi_coherence import phi_coherence


STAMP = "2026-09-22T00:00:00Z"


def test_empty_phi_has_zero_coherence():
    phi = create_phi_structure([])

    assert phi_coherence(phi) == 0.0


def test_single_component_phi_has_full_coherence():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    c = create_genesis("c", STAMP)
    first = create_relation(a.id, b.id, "knows", STAMP)
    second = create_relation(b.id, c.id, "knows", STAMP)

    phi = create_phi_structure([first, second])

    assert phi_coherence(phi) == 1.0


def test_disconnected_phi_uses_largest_component():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    c = create_genesis("c", STAMP)
    d = create_genesis("d", STAMP)
    first = create_relation(a.id, b.id, "knows", STAMP)
    second = create_relation(c.id, d.id, "knows", STAMP)

    phi = create_phi_structure([first, second])

    assert phi_coherence(phi) == pytest.approx(0.5)


def test_relation_order_does_not_change_coherence():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    c = create_genesis("c", STAMP)
    first = create_relation(a.id, b.id, "knows", STAMP)
    second = create_relation(b.id, c.id, "supports", STAMP)

    left = create_phi_structure([first, second])
    right = create_phi_structure([second, first])

    assert phi_coherence(left) == phi_coherence(right)


def test_wrong_type_is_rejected():
    with pytest.raises(TypeError):
        phi_coherence(object())
