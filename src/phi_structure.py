"""Minimal immutable structural fingerprint for theNet."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class PhiStructure:
    id: str
    relation_ids: tuple[str, ...]
    version: int = 1


def _canonical(relation_ids: tuple[str, ...]) -> str:
    return json.dumps(
        {"relation_ids": relation_ids, "version": 1},
        sort_keys=True,
        separators=(",", ":"),
    )


def create_phi_structure(relation_ids: Sequence[str]) -> PhiStructure:
    if isinstance(relation_ids, (str, bytes)) or not isinstance(
        relation_ids, Sequence
    ):
        raise ValueError("relation_ids must be a sequence")

    values = tuple(relation_ids)
    for index, relation_id in enumerate(values):
        if not isinstance(relation_id, str) or not relation_id.strip():
            raise ValueError(
                f"relation_ids[{index}] must be a non-empty string"
            )

    identifier = sha256(_canonical(values).encode("utf-8")).hexdigest()

    return PhiStructure(id=identifier, relation_ids=values)
