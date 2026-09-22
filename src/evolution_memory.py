"""Verified Agent Ω evolution to Ω² memory integration."""

from __future__ import annotations

from dataclasses import dataclass

from src.collective_evolution import CollectiveEvolution
from src.memory import MemoryRecord, create_memory


@dataclass(frozen=True)
class EvolutionMemory:
    evolution: CollectiveEvolution
    memory: MemoryRecord


def record_verified_evolution_memory(
    evolution: CollectiveEvolution,
    subject_id: str,
    created_at: str,
) -> EvolutionMemory:
    if not isinstance(evolution, CollectiveEvolution):
        raise ValueError("evolution must be CollectiveEvolution")
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    memory = create_memory(
        subject_id=subject_id,
        source_id=evolution.commit.id,
        kind="verified-evolution",
        created_at=created_at,
    )
    return EvolutionMemory(evolution=evolution, memory=memory)
