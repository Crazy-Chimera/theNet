from src.gamma import create_convergence
from src.genesis import create_genesis
from src.omega import create_omega_transition
from src.omega2 import create_omega_memory
from src.phi import create_phi
from src.relation import create_relation
from src.resonance import create_resonance


STAMP = "2026-09-21T00:00:00Z"


def test_foundational_chain_genesis_relation_phi_omega_memory_resonance_gamma():
    source = create_genesis("agent:a", STAMP)
    target = create_genesis("agent:b", STAMP)

    relation = create_relation(
        source.id,
        target.id,
        "observation",
        STAMP,
    )
    structure = create_phi([relation])
    transition = create_omega_transition(
        structure.id,
        source.id,
        "verified structural evolution",
        STAMP,
    )
    memory = create_omega_memory(transition.id, transition.to_state, STAMP)
    resonance = create_resonance(structure.id, memory.id, STAMP)
    convergence = create_convergence(
        [source.id, source.id],
        source.id,
    )

    assert relation.source_id == source.id
    assert relation.target_id == target.id
    assert structure.relation_ids == (relation.id,)
    assert structure.node_ids == tuple(sorted((source.id, target.id)))
    assert transition.from_state == structure.id
    assert transition.to_state == source.id
    assert memory.transition_id == transition.id
    assert memory.state_id == source.id
    assert resonance.structure_id == structure.id
    assert resonance.memory_id == memory.id
    assert convergence.converged is True
    assert convergence.resolved_id == source.id


def test_foundational_chain_preserves_immutable_boundaries():
    source = create_genesis("agent:a", STAMP)
    target = create_genesis("agent:b", STAMP)
    relation = create_relation(source.id, target.id, "observation", STAMP)
    structure = create_phi([relation])

    assert source.relations == ()
    assert target.relations == ()
    assert structure.relation_ids == (relation.id,)
