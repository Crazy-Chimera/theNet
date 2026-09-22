import pytest

from src.agent_state import create_agent_state
from src.collective_evolution import evolve_collectively
from src.evolution_memory import record_verified_evolution_memory
from src.evolution_resonance import create_evolution_resonance
from src.genesis import create_genesis
from src.proposal import create_proposal
from src.relation import create_relation
from src.structure import create_phi_structure
from src.verification import create_verification


STAMP = "2026-09-22T13:00:00Z"


def build_context():
    proposer = create_genesis("agent-1", STAMP)
    verifier = create_genesis("agent-2", STAMP)
    relation = create_relation(proposer.id, verifier.id, "relates", STAMP)
    structure = create_phi_structure([relation])

    state = create_agent_state(proposer.id, "singularity-0", STAMP)
    proposal = create_proposal(proposer.id, state.id, "change", STAMP)
    verification = create_verification(
        proposal.id,
        verifier.id,
        "evidence",
        True,
        STAMP,
    )
    evolution = evolve_collectively(
        state,
        proposal,
        [verification],
        quorum=1,
        new_singularity_id="singularity-1",
        created_at=STAMP,
    )
    memory = record_verified_evolution_memory(evolution, proposer.id, STAMP)
    return structure, memory


def test_resonance_binds_phi_to_verified_evolution_memory():
    structure, memory = build_context()

    resonance = create_evolution_resonance(structure, memory, STAMP)

    assert resonance.structure_id == structure.id
    assert resonance.memory_id == memory.memory.id


def test_resonance_is_deterministic():
    structure, memory = build_context()

    first = create_evolution_resonance(structure, memory, STAMP)
    second = create_evolution_resonance(structure, memory, STAMP)

    assert first == second


@pytest.mark.parametrize("created_at", ["", "   "])
def test_empty_resonance_timestamp_is_rejected(created_at):
    structure, memory = build_context()

    with pytest.raises(ValueError):
        create_evolution_resonance(structure, memory, created_at)
