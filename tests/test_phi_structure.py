from src.phi_structure import create_phi_structure


def test_empty_structure_is_valid_and_deterministic():
    first = create_phi_structure(())
    second = create_phi_structure(())
    assert first.relation_ids == ()
    assert first.id == second.id


def test_structure_preserves_order():
    structure = create_phi_structure(["r1", "r2"])
    assert structure.relation_ids == ("r1", "r2")


def test_same_input_has_same_identity():
    assert create_phi_structure(["r1", "r2"]).id == create_phi_structure(
        ["r1", "r2"]
    ).id


def test_order_changes_identity():
    assert create_phi_structure(["r1", "r2"]).id != create_phi_structure(
        ["r2", "r1"]
    ).id


def test_membership_changes_identity():
    assert create_phi_structure(["r1"]).id != create_phi_structure(
        ["r1", "r2"]
    ).id


def test_invalid_container_is_rejected():
    try:
        create_phi_structure("r1")
    except ValueError:
        pass
    else:
        raise AssertionError("string input must be rejected")


def test_invalid_relation_identifier_is_rejected():
    try:
        create_phi_structure(["r1", ""])
    except ValueError:
        pass
    else:
        raise AssertionError("empty relation identifier must be rejected")


def test_structure_is_immutable():
    structure = create_phi_structure(["r1"])
    try:
        structure.relation_ids = ("r2",)
    except AttributeError:
        pass
    else:
        raise AssertionError("structure must be immutable")


def test_input_is_not_mutated():
    relation_ids = ["r1", "r2"]
    create_phi_structure(relation_ids)
    assert relation_ids == ["r1", "r2"]
