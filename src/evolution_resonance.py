"""ΦΩ² resonance integration for verified Agent Ω evolution memory."""

from __future__ import annotations

from src.evolution_memory import EvolutionMemory
from src.resonance import Resonance, create_resonance
from src.structure import PhiStructure


def create_evolution_resonance(
    structure: PhiStructure,
    evolution_memory: EvolutionMemory,
    created_at: str,
) -> Resonance:
    if not isinstance(structure, PhiStructure):
        raise ValueError("structure must be PhiStructure")
    if not isinstance(evolution_memory, EvolutionMemory):
        raise ValueError("evolution_memory must be EvolutionMemory")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    return create_resonance(
        structure_id=structure.id,
        memory_id=evolution_memory.memory.id,
        created_at=created_at,
    )
