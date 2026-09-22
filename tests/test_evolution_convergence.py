from dataclasses import FrozenInstanceError

import pytest

from src.collective_evolution import create_collective_evolution
from src.evolution_convergence import EvolutionConvergence, create_evolution_convergence
from src.evolution_memory import record_verified_evolution_memory
from src.evolution_resonance import create_evolution_resonance
from src.resonance import Resonance
from src.structure import create_phi_structure
from src.relation import create_relation


STAMP = "2026-09-22T00:10:00Z"


def make_context():
    relation = create_relation("agent-a", "agent-b", "connect", STAMP)
    structure = create_phi_structure([relation])
    evolution = create_collective_evolution(
        proposals=["proposal-a"],
        selected_proposal="proposal-a",
        created_at=STAMP,
    )
    memory = record_verified_evolution_memory(evolution, "agent-a", STAMP)
    resonance = create_evolution_resonance(structure, memory, STAMP)
    return resonance


def test_binds_resonance_to_explicit_convergence():
    resonance = make_context()
    result = create_evolution_convergence(resonance, ["state-b", "state-a"], "state-a", STAMP)

    assert isinstance(result, EvolutionConvergence)
    assert isinstance(result.resonance, Resonance)
    assert result.resonance.id == resonance.id
    assert result.convergence.selected_state == "state-a"
    assert result.convergence.candidate_states == ("state-a", "state-b")


def test_equal_inputs_are_deterministic():
    resonance = make_context()
    left = create_evolution_convergence(resonance, ["b", "a"], "a", STAMP)
    right = create_evolution_convergence(resonance, ["a", "b"], "a", STAMP)

    assert left == right
    assert left.convergence.id == right.convergence.id


def test_resonance_type_is_required():
    with pytest.raises(ValueError):
        create_evolution_convergence(object(), ["a"], "a", STAMP)


def test_invalid_convergence_is_rejected():
    resonance = make_context()
    with pytest.raises(ValueError):
        create_evolution_convergence(resonance, ["a", "b"], "c", STAMP)


def test_timestamp_is_required():
    resonance = make_context()
    with pytest.raises(ValueError):
        create_evolution_convergence(resonance, ["a"], "a", "")


def test_result_is_immutable():
    resonance = make_context()
    result = create_evolution_convergence(resonance, ["a"], "a", STAMP)

    with pytest.raises(FrozenInstanceError):
        result.created_at = "changed"
