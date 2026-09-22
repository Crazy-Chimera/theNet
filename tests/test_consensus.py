from dataclasses import FrozenInstanceError

import pytest

from src.consensus import create_consensus
from src.proposal import create_proposal
from src.verification import create_verification


STAMP = "2026-09-22T14:00:00Z"


def _proposal():
    return create_proposal("agent:a", "state:1", "adopt", STAMP)


def test_quorum_one_can_reach_consensus():
    proposal = _proposal()
    verification = create_verification(
        proposal.id, "agent:b", "evidence:b", True, STAMP
    )

    consensus = create_consensus(proposal.id, [verification], 1)

    assert consensus.reached is True
    assert consensus.verifier_ids == ("agent:b",)


def test_higher_quorum_requires_distinct_verifiers():
    proposal = _proposal()
    first = create_verification(
        proposal.id, "agent:b", "evidence:b", True, STAMP
    )

    consensus = create_consensus(proposal.id, [first], 2)

    assert consensus.reached is False


def test_two_independent_verifiers_reach_quorum_two():
    proposal = _proposal()
    first = create_verification(
        proposal.id, "agent:b", "evidence:b", True, STAMP
    )
    second = create_verification(
        proposal.id, "agent:c", "evidence:c", True, "2026-09-22T14:00:01Z"
    )

    consensus = create_consensus(proposal.id, [first, second], 2)

    assert consensus.reached is True
    assert consensus.verifier_ids == ("agent:b", "agent:c")


def test_invalid_or_mismatched_verification_is_rejected():
    proposal = _proposal()
    invalid = create_verification(
        proposal.id, "agent:b", "evidence:b", False, STAMP
    )
    other = create_proposal("agent:a", "state:1", "different proposal", STAMP)

    with pytest.raises(ValueError):
        create_consensus(proposal.id, [invalid], 1)

    mismatched = create_verification(
        other.id, "agent:c", "evidence:c", True, STAMP
    )
    with pytest.raises(ValueError):
        create_consensus(proposal.id, [mismatched], 1)


def test_same_verifier_cannot_count_twice():
    proposal = _proposal()
    first = create_verification(
        proposal.id, "agent:b", "evidence:b", True, STAMP
    )
    second = create_verification(
        proposal.id, "agent:b", "different evidence", True, "2026-09-22T14:00:01Z"
    )

    with pytest.raises(ValueError):
        create_consensus(proposal.id, [first, second], 2)


def test_consensus_is_immutable_and_deterministic():
    proposal = _proposal()
    first = create_verification(
        proposal.id, "agent:b", "evidence:b", True, STAMP
    )
    second = create_verification(
        proposal.id, "agent:c", "evidence:c", True, "2026-09-22T14:00:01Z"
    )

    left = create_consensus(proposal.id, [first, second], 2)
    right = create_consensus(proposal.id, [second, first], 2)

    assert left == right
    with pytest.raises(FrozenInstanceError):
        left.quorum = 3
