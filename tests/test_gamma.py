from dataclasses import FrozenInstanceError

import pytest

from src.gamma import create_convergence

def test_exact_agreement_converges():
    result = create_convergence(["state:a", "state:a", "state:a"])
    assert result.converged is True
    assert result.resolved_id == "state:a"

def test_conflict_does_not_choose_winner():
    result = create_convergence(["state:a", "state:b", "state:a"])
    assert result.converged is False
    assert result.resolved_id is None
    assert result.proposal_ids == ("state:a", "state:a", "state:b")

def test_order_does_not_change_identity():
    left = create_convergence(["state:b", "state:a"])
    right = create_convergence(["state:a", "state:b"])
    assert left == right

def test_multiplicity_is_preserved():
    repeated = create_convergence(["state:a", "state:a", "state:b"])
    unique = create_convergence(["state:a", "state:b"])
    assert repeated.id != unique.id

@pytest.mark.parametrize('proposals', [[], [''], [None]])
def test_invalid_proposals_are_rejected(proposals):
    with pytest.raises(ValueError):
        create_convergence(proposals)

def test_convergence_is_immutable():
    result = create_convergence(["state:a"])
    with pytest.raises(FrozenInstanceError):
        result.converged = False