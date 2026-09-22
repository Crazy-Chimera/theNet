from dataclasses import FrozenInstanceError

import pytest

from src.agent_state import create_agent_state
from src.collective_evolution import evolve_collectively
from src.evolution_memory import (
    EvolutionMemory,
    record_verified_evolution_memory,
)
from src.genesis import create_genesis
from src.proposal import create_proposal
from src.verification import create_verification


STAMP = "2026-09-22T12:00:00Z"


def build_evolution():
    proposer = create_genesis("agent-1", STAMP)
    verifier = create_genesis("agent-2", STAMP)
    state = create_agent_state(proposer.id, "singularity-0", STAMP)
    proposal = create_proposal(
        proposer.id,
        state.id,
        "verified change",
        STAMP,
    )
    verification = create_verification(
        proposal.id,
        verifier.id,
        "evidence",
        True,
        STAMP,
    )
    return evolve_collectively(
        state,
        proposal,
        [verification],
        quorum=1,
        new_singularity_id="singularity-1",
        created_at=STAMP,
    )


def test_verified_evolution_is_persisted_as_memory():
    evolution = build_evolution()

    result = record_verified_evolution_memory(
        evolution,
        subject_id="agent-1",
        created_at=STAMP,
    )

    assert isinstance(result, EvolutionMemory)
    assert result.memory.source_id == evolution.commit.id
    assert result.memory.subject_id == "agent-1"
    assert result.memory.kind == "verified-evolution"


def test_memory_identity_is_deterministic():
    evolution = build_evolution()

    first = record_verified_evolution_memory(evolution, "agent-1", STAMP)
    second = record_verified_evolution_memory(evolution, "agent-1", STAMP)

    assert first.memory.id == second.memory.id


@pytest.mark.parametrize(
    "subject_id,created_at",
    [
        ("", STAMP),
        ("agent-1", ""),
    ],
)
def test_invalid_memory_inputs_are_rejected(subject_id, created_at):
    with pytest.raises(ValueError):
        record_verified_evolution_memory(
            build_evolution(),
            subject_id,
            created_at,
        )


def test_memory_integration_result_is_immutable():
    result = record_verified_evolution_memory(
        build_evolution(),
        "agent-1",
        STAMP,
    )

    with pytest.raises(FrozenInstanceError):
        result.memory = None
