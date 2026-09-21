"""Minimal immutable ΦΩ² resonance primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class Resonance:
    id: str
    structure_id: str
    memory_id: str
    created_at: str
    version: int = 1

def _canonical(structure_id: str, memory_id: str, created_at: str) -> str:
    return json.dumps(
        {
            "created_at": created_at,
            "memory_id": memory_id,
            "structure_id": structure_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )

def create_resonance(structure_id: str, memory_id: str, created_at: str) -> Resonance:
    for name, value in {
        "structure_id": structure_id,
        "memory_id": memory_id,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    identifier = sha256(_canonical(structure_id, memory_id, created_at).encode('utf-8')).hexdigest()
    return Resonance(identifier, structure_id, memory_id, created_at)