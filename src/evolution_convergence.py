"""Γ convergence integration for verified Agent Ω evolution resonance."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from src.convergence import Convergence, create_convergence
from src.resonance import Resonance


@dataclass(frozen=True)
class EvolutionConvergence:
    resonance: Resonance
    convergence: Convergence
    created_at: str


def create_evolution_convergence(
    resonance: Resonance,
    candidates: Iterable[str],
    selected_state: str,
    created_at: str,
) -> EvolutionConvergence:
    if not isinstance(resonance, Resonance):
        raise ValueError("resonance must be Resonance")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    convergence = create_convergence(candidates, selected_state, created_at)
    return EvolutionConvergence(
        resonance=resonance,
        convergence=convergence,
        created_at=created_at,
    )
