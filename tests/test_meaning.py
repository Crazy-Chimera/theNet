from dataclasses import FrozenInstanceError

import pytest

from src.meaning import create_meaning

STAMP = '2026-09-21T00:10:00Z'

def test_create_meaning():
    meaning = create_meaning('convergence:a', 'contribution:b', STAMP)
    assert meaning.convergence_id == 'convergence:a'
    assert meaning.contribution_id == 'contribution:b'
    assert meaning.created_at == STAMP
    assert meaning.version == 1
    assert len(meaning.id) == 64

def test_meaning_is_deterministic():
    assert create_meaning('convergence:a', 'contribution:b', STAMP) == create_meaning('convergence:a', 'contribution:b', STAMP)

@pytest.mark.parametrize('values', [('', 'contribution:b', STAMP), ('convergence:a', '', STAMP), ('convergence:a', 'contribution:b', '')])
def test_empty_fields_are_rejected(values):
    with pytest.raises(ValueError):
        create_meaning(*values)

def test_meaning_identity_changes_with_contribution():
    left = create_meaning('convergence:a', 'contribution:b', STAMP)
    right = create_meaning('convergence:a', 'contribution:c', STAMP)
    assert left.id != right.id

def test_meaning_is_immutable():
    meaning = create_meaning('convergence:a', 'contribution:b', STAMP)
    with pytest.raises(FrozenInstanceError):
        meaning.contribution_id = 'other'