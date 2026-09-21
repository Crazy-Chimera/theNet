"""Minimal deterministic Genesis state for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class GenesisState:
    id: str
    subject: str
    created_at: str
    relations: tuple[str, ...]
    version: int = 1


def _canonical(subject: str, created_at: str) -> str:
    return json.dumps(
        {"created_at": created_at, "subject": subject, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_genesis(subject: str, created_at: str) -> GenesisState:
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("subject must be non-empty")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("created_at must be non-empty")

    canonical = _canonical(subject, created_at)
    identifier = sha256(canonical.encode("utf-8")).hexdigest()

    return GenesisState(
        id=identifier,
        subject=subject,
        created_at=created_at,
        relations=(),
    )
