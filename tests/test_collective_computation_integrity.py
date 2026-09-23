from dataclasses import replace

from src.agent_state import create_agent_state
from src.collective_computation import run_collective_computation_cycle
from src.collective_computation_integrity import verify_collective_computation_integrity
from src.genesis import create_genesis
from src.memory import create_memory
from src.proposal import create_proposal
from src.resource_state import create_resource_state
from src.verification import create_verification


STAMP = "2026-09-23T10:00:00Z"


def _cycle():
    agent = create_genesis("agent-a", STAMP)
    verifier = create_genesis("agent-b", STAMP)
    state = create_agent_state(agent.id, "singularity-a", STAMP)
    proposal = create_proposal(agent.id, state.id, "verified relational computation", STAMP)
    verification = create_verification(
        proposal.id, verifier.id, "evidence-b", True, STAMP
    )
    return run_collective_computation_cycle(
        state,
        proposal,
        (verification,),
        1,
        "singularity-b",
        STAMP,
        create_resource_state(100.0, 0.0, STAMP),
        create_resource_state(100.0, 0.0, STAMP),
    )


def test_integrity_accepts_completed_cycle():
    assert verify_collective_computation_integrity(_cycle()) is True


def test_integrity_is_deterministic():
    assert verify_collective_computation_integrity(_cycle()) is True


def test_integrity_rejects_wrong_memory_source():
    cycle = _cycle()
    fake_memory = create_memory(
        cycle.memory.subject_id,
        "wrong-source",
        cycle.memory.kind,
        STAMP,
    )
    assert verify_collective_computation_integrity(
        replace(cycle, memory=fake_memory)
    ) is False


def test_integrity_rejects_unverified_utility():
    cycle = _cycle()
    utility = replace(cycle.utility, verified=False)
    assert verify_collective_computation_integrity(
        replace(cycle, utility=utility)
    ) is False


def test_integrity_rejects_wrong_resource_type():
    cycle = _cycle()
    assert verify_collective_computation_integrity(
        replace(cycle, memory_resource=object())
    ) is False


def test_integrity_rejects_non_cycle_input():
    assert verify_collective_computation_integrity(object()) is False
