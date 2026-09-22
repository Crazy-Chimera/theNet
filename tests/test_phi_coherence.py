import pytest

from src.genesis import create_genesis
from src.relation import create_relation
from src.structure import create_phi_structure
from src.phi_coherence import phi_coherence


STAMP = "2026-09-22T00:00:00Z"


def test_empty_phi_has_zero_coherence():
    phi = create_phi_structure([])

    assert phi_coherence(phi) == 0.0


def test_non_empty_canonical_phi_has_full_coherence():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    relation = create_relation(a.id, b.id, "knows", STAMP)

    phi = create_phi_structure([relation])

    assert phi_coherence(phi) == 1.0


def test_coherence_is_deterministic():
    a = create_genesis("a", STAMP)
    b = create_genesis("b", STAMP)
    relation = create_relation(a.id, b.id, "knows", STAMP)
    phi = create_phi_structure([relation])

    assert phi_coherence(phi) == phi_coherence(phi)


def test_wrong_type_is_rejected():
    with pytest.raises(TypeError):
        phi_coherence(object())
