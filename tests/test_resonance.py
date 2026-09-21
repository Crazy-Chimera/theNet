from dataclasses import FrozenInstanceError

import pytest

from src.resonance import create_resonance


STAMP = "2026-09-21T00:05:00Z"


def test_create_resonance():
    resonance = create_resonance("structure:a", "memory:b", STAMP)

    assert resonance.structure_id == "structure:a"
    assert resonance.memory_id == "memory:b"
    assert resonance.created_at == STAMP
    assert resonance.version == 1
    assert len(resonance.id) == 64


def test_resonance_is_deterministic():
    first = create_resonance("structure:a", "memory:b", STAMP)
    second = create_resonance("structure:a", "memory:b", STAMP)

    assert first == second


@pytest.mark.parametrize(
    ("structure_id", "memory_id", "created_at"),
    [
        ("", "memory:b", STAMP),
        ("structure:a", "", STAMP),
        ("structure:a", "memory:b", ""),
    ],
)
def test_empty_fields_are_rejected(structure_id, memory_id, created_at):
    with pytest.raises(ValueError):
        create_resonance(structure_id, memory_id, created_at)


def test_resonance_is_immutable():
    resonance = create_resonance("structure:a", "memory:b", STAMP)

    with pytest.raises(FrozenInstanceError):
        resonance.memory_id = "memory:c"


def test_structure_change_changes_identity():
    first = create_resonance("structure:a", "memory:b", STAMP)
    second = create_resonance("structure:b", "memory:b", STAMP)

    assert first.id != second.id


def test_memory_change_changes_identity():
    first = create_resonance("structure:a", "memory:b", STAMP)
    second = create_resonance("structure:a", "memory:c", STAMP)

    assert first.id != second.id
