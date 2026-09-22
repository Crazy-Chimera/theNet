from src.genesis import create_genesis
from src.omega2 import create_omega_memory
from src.relation import create_relation
from src.phi import create_phi
from src.resonance import create_resonance


def test_phi_omega2_resonance_binds_real_structure_and_memory() -> None:
    a = create_genesis("a", "2026-09-22T08:00:00Z")
    b = create_genesis("b", "2026-09-22T08:00:00Z")
    relation = create_relation(a.id, b.id, "knows", "2026-09-22T08:01:00Z")
    structure = create_phi([relation])
    memory = create_omega_memory(
        "transition:1",
        a.id,
        "2026-09-22T08:02:00Z",
    )

    resonance = create_resonance(
        structure.id,
        memory.id,
        "2026-09-22T08:03:00Z",
    )

    assert resonance.structure_id == structure.id
    assert resonance.memory_id == memory.id
    assert len(resonance.id) == 64
