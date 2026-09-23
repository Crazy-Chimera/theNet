import pytest

from src.agent_state import create_agent_state
from src.collective_computation import run_collective_computation_cycle
from src.genesis import create_genesis
from src.proposal import create_proposal
from src.resource_state import create_resource_state
from src.verification import create_verification


STAMP = "2026-09-23T10:00:00Z"


def _cycle(quorum=1):
    agent = create_genesis("agent-a", STAMP)
    verifier = create_genesis("agent-b", STAMP)
    state = create_agent_state(agent.id, "singularity-a", STAMP)
    proposal = create_proposal(
        agent.id,
        state.id,
        "verified relational computation",
        STAMP,
    )
    verification = create_verification(
        proposal.id,
        verifier.id,
        "evidence-b",
        True,
        STAMP,
    )
    return run_collective_computation_cycle(
        state,
        proposal,
        (verification,),
        quorum,
        "singularity-b",
        STAMP,
        create_resource_state(100.0, 0.0, STAMP),
        create_resource_state(100.0, 0.0, STAMP),
    )


def test_cycle_connects_evolution_memory_phi_and_resources():
    result = _cycle()

    assert result.evolution.state.version == 2
    assert result.memory.source_id == result.evolution.commit.id
    assert result.utility.verified is True
    assert result.utility.evidence_ids == (result.memory.id,)
    assert result.phi.relation_ids == (result.relations[0].id,)
    assert result.memory_resource.used > 0.0
    assert result.compute_resource.used > 0.0


def test_cycle_is_deterministic():
    assert _cycle() == _cycle()


def test_cycle_requires_quorum():
    with pytest.raises(ValueError, match="quorum"):
        _cycle(quorum=2)


def test_cycle_rejects_self_verification():
    agent = create_genesis("agent-a", STAMP)
    state = create_agent_state(agent.id, "singularity-a", STAMP)
    proposal = create_proposal(agent.id, state.id, "self verify", STAMP)
    verification = create_verification(
        proposal.id,
        agent.id,
        "self-evidence",
        True,
        STAMP,
    )

    with pytest.raises(ValueError, match="proposer"):
        run_collective_computation_cycle(
            state,
            proposal,
            (verification,),
            1,
            "singularity-b",
            STAMP,
            create_resource_state(100.0, 0.0, STAMP),
            create_resource_state(100.0, 0.0, STAMP),
        )


def test_cycle_requires_resources_to_be_valid():
    agent = create_genesis("agent-a", STAMP)
    verifier = create_genesis("agent-b", STAMP)
    state = create_agent_state(agent.id, "singularity-a", STAMP)
    proposal = create_proposal(agent.id, state.id, "resource test", STAMP)
    verification = create_verification(
        proposal.id,
        verifier.id,
        "evidence-b",
        True,
        STAMP,
    )

    with pytest.raises((TypeError, ValueError)):
        run_collective_computation_cycle(
            state,
            proposal,
            (verification,),
            1,
            "singularity-b",
            STAMP,
            object(),
            create_resource_state(100.0, 0.0, STAMP),
        )
