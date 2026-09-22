"""Minimal immutable Ω² memory primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    subject_id: str
    source_id: str
    kind: str
    created_at: str
    version: int = 1


def create_memory(
    subject_id: str,
    source_id: str,
    kind: str,
    created_at: str,
) -> MemoryRecord:
    values = {
        "subject_id": subject_id,
        "source_id": source_id,
        "kind": kind,
        "created_at": created_at,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    canonical = json.dumps(
        {
            "created_at": created_at,
            "kind": kind,
            "source_id": source_id,
            "subject_id": subject_id,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    return MemoryRecord(
        id=sha256(canonical.encode("utf-8")).hexdigest(),
        subject_id=subject_id,
        source_id=source_id,
        kind=kind,
        created_at=created_at,
    )
