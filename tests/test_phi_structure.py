from dataclasses import FrozenInstanceError

import pytest

from src.phi_structure import create_phi_structure


def test_create_phi_structure():
    structure = create_phi_structure("subject-1", ["r2", "r1"])
    assert structure.subject_id == "subject-1"
    assert structure.relation_ids == ("r1", "r2")
    assert len(structure.id) == 64
    assert structure.version == 1


def test_relation_order_does_not_change_identity():
    a = create_phi_structure("subject-1", ["r1", "r2"])
    b = create_phi_structure("subject-1", ["r2", "r1"])
    assert a.id == b.id
    assert a == b


def test_duplicate_relations_are_collapsed():
    a = create_phi_structure("subject-1", ["r1", "r1", "r2"])
    b = create_phi_structure("subject-1", ["r2", "r1"])
    assert a.relation_ids == ("r1", "r2")
    assert a.id == b.id


@pytest.mark.parametrize("subject_id", ["", "   ", None, 42])
def test_invalid_subject_is_rejected(subject_id):
    with pytest.raises(ValueError):
        create_phi_structure(subject_id, [])


@pytest.mark.parametrize(
    "relation_ids",
    [None, "r1", [""], ["r1", None]],
)
def test_invalid_relation_ids_are_rejected(relation_ids):
    with pytest.raises(ValueError):
        create_phi_structure("subject-1", relation_ids)


def test_structural_change_changes_identity():
    a = create_phi_structure("subject-1", ["r1"])
    b = create_phi_structure("subject-1", ["r1", "r2"])
    c = create_phi_structure("subject-2", ["r1"])
    assert a.id != b.id
    assert a.id != c.id


def test_output_is_immutable():
    structure = create_phi_structure("subject-1", ["r1"])
    with pytest.raises(FrozenInstanceError):
        structure.subject_id = "subject-2"
