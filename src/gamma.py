"""Minimal deterministic exact-convergence primitive for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

@dataclass(frozen=True)
class Convergence:
    id: str
    proposal_ids: tuple[str, ...]
    resolved_id: str | None
    converged: bool
    version: int = 1

def _canonical(proposal_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "proposal_ids": proposal_ids,
            "version": 1,
        },
        sort_keys=True,
        separators=(",", ":"),
    )

def create_convergence(proposals: Iterable[str]) -> Convergence:
    proposal_ids = tuple(sorted(tuple(proposals)))
    if not proposal_ids:
        raise ValueError("proposals must be non-empty")
    if any(not isinstance(value, str) or not value.strip() for value in proposal_ids):
        raise ValueError("proposal IDs must be non-empty strings")

    converged = len(set(proposal_ids)) == 1
    resolved_id = proposal_ids[0] if converged else None
    identifier = sha256(_canonical(proposal_ids).encode('utf-8')).hexdigest()
    return Convergence(identifier, proposal_ids, resolved_id, converged)