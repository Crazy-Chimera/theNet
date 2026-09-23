import pytest

from src.agent_state import create_agent_state
from src.collective_evolution import evolve_collectively
from src.genesis import create_genesis
from src.proposal import create_proposal
from src.verification import create_verification


def _fixture():
    source = create_genesis("agent-1", "2026-09-22T00:00:00Z")
    verifier_2 = create_genesis("agent-2", "2026-09-22T00:00:00Z")
    verifier_3 = create_genesis("agent-3", "2026-09-22T00:00:00Z")
    state = create_agent_state(source.id, "singularity-0", "2026-09-22T00:00:00Z")
    proposal = create_proposal(
        source.id,
        state.id,
        "learn verified relation",
        "2026-09-22T00:01:00Z",
    )
    verifications = [
        create_verification(
            proposal.id,
            verifier_2.id,
            "evidence-2",
            True,
            "2026-09-22T00:02:00Z",
        ),
        create_verification(
            proposal.id,
            verifier_3.id,
            "evidence-3",
            True,
            "2026-09-22T00:03:00Z",
        ),
    ]
    return state, proposal, verifications


def test_collective_evolution_requires_and_reaches_quorum():
    state, proposal, verifications = _fixture()

    result = evolve_collectively(
        state,
        proposal,
        verifications,
        quorum=2,
        new_singularity_id="singularity-1",
        created_at="2026-09-22T00:04:00Z",
    )

    assert result.consensus.reached is True
    assert len(result.consensus.verifier_ids) == 2
    assert result.commit.previous_state_id == state.id
    assert result.state.version == state.version + 1
    assert result.state.id != state.id


def test_collective_evolution_rejects_insufficient_quorum():
    state, proposal, verifications = _fixture()

    with pytest.raises(ValueError, match="quorum"):
        evolve_collectively(
            state,
            proposal,
            verifications[:1],
            quorum=2,
            new_singularity_id="singularity-1",
            created_at="2026-09-22T00:04:00Z",
        )


def test_quorum_one_allows_single_verifier():
    state, proposal, verifications = _fixture()

    result = evolve_collectively(
        state,
        proposal,
        verifications[:1],
        quorum=1,
        new_singularity_id="singularity-1",
        created_at="2026-09-22T00:04:00Z",
    )

    assert result.consensus.reached is True
    assert len(result.consensus.verifier_ids) == 1


def test_collective_evolution_rejects_invalid_verification():
    state, proposal, verifications = _fixture()
    invalid = create_verification(
        proposal.id,
        "invalid-verifier",
        "bad evidence",
        False,
        "2026-09-22T00:03:00Z",
    )

    with pytest.raises(ValueError, match="valid"):
        evolve_collectively(
            state,
            proposal,
            [verifications[0], invalid],
            quorum=2,
            new_singularity_id="singularity-1",
            created_at="2026-09-22T00:04:00Z",
        )


def test_collective_evolution_rejects_proposal_for_wrong_state():
    state, proposal, verifications = _fixture()
    wrong_state = create_agent_state(
        state.subject_id,
        "other-singularity",
        "2026-09-22T00:05:00Z",
    )
    wrong_proposal = create_proposal(
        proposal.proposer_id,
        wrong_state.id,
        proposal.proposal,
        "2026-09-22T00:06:00Z",
    )
    wrong_verifications = [
        create_verification(
            wrong_proposal.id,
            "verifier-1",
            "evidence",
            True,
            "2026-09-22T00:07:00Z",
        ),
    ]

    with pytest.raises(ValueError, match="proposal"):
        evolve_collectively(
            state,
            wrong_proposal,
            wrong_verifications,
            quorum=1,
            new_singularity_id="singularity-1",
            created_at="2026-09-22T00:08:00Z",
        )


def test_collective_evolution_rejects_proposer_self_verification():
    state, proposal, _ = _fixture()
    self_verification = create_verification(
        proposal.id,
        proposal.proposer_id,
        "self-attestation",
        True,
        "2026-09-22T00:03:00Z",
    )

    with pytest.raises(ValueError, match="cannot verify"):
        evolve_collectively(
            state,
            proposal,
            [self_verification],
            quorum=1,
            new_singularity_id="singularity-1",
            created_at="2026-09-22T00:04:00Z",
        )


def test_collective_evolution_rejects_replayed_proposal():
    state, proposal, verifications = _fixture()
    first = evolve_collectively(
        state,
        proposal,
        verifications,
        quorum=2,
        new_singularity_id="singularity-1",
        created_at="2026-09-22T00:04:00Z",
    )

    with pytest.raises(ValueError, match="already been applied"):
        evolve_collectively(
            state,
            proposal,
            verifications,
            quorum=2,
            new_singularity_id="singularity-1",
            created_at="2026-09-22T00:05:00Z",
            prior_commits=[first.commit],
        )
