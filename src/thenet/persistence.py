"""PostgreSQL persistence lifecycle for Genesis and Relation."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass

import psycopg

from genesis import create_genesis
from relation import create_relation


@dataclass(frozen=True)
class PersistenceResult:
    genesis_id: str
    relation_id: str
    loaded_genesis_id: str
    loaded_relation_id: str

    @property
    def persisted(self) -> bool:
        return (
            self.genesis_id == self.loaded_genesis_id
            and self.relation_id == self.loaded_relation_id
        )

    def __str__(self) -> str:
        return json.dumps(
            {
                "genesis_id": self.genesis_id,
                "relation_id": self.relation_id,
                "loaded_genesis_id": self.loaded_genesis_id,
                "loaded_relation_id": self.loaded_relation_id,
                "persisted": self.persisted,
            },
            sort_keys=True,
        )


def _database_url() -> str:
    value = os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence")
    return value


def _ids() -> tuple[str, str]:
    genesis = create_genesis(
        "theNet-persistence-probe",
        "2026-09-30T09:00:00+02:00",
    )
    relation = create_relation(
        genesis.id,
        genesis.id,
        "self-observation",
        "2026-09-30T09:00:01+02:00",
    )
    return genesis.id, relation.id


def run_persistence_probe() -> PersistenceResult:
    genesis_id, relation_id = _ids()

    with psycopg.connect(_database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS thenet_persistence_probe (
                    probe_key TEXT PRIMARY KEY,
                    genesis_id TEXT NOT NULL,
                    relation_id TEXT NOT NULL,
                    payload_hash TEXT NOT NULL
                )
                """
            )

            payload = f"{genesis_id}:{relation_id}".encode("utf-8")
            cursor.execute(
                """
                INSERT INTO thenet_persistence_probe
                    (probe_key, genesis_id, relation_id, payload_hash)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (probe_key) DO UPDATE
                SET genesis_id = EXCLUDED.genesis_id,
                    relation_id = EXCLUDED.relation_id,
                    payload_hash = EXCLUDED.payload_hash
                """,
                (
                    "genesis-relation-v1",
                    genesis_id,
                    relation_id,
                    hashlib.sha256(payload).hexdigest(),
                ),
            )
            connection.commit()

            cursor.execute(
                """
                SELECT genesis_id, relation_id
                FROM thenet_persistence_probe
                WHERE probe_key = %s
                """,
                ("genesis-relation-v1",),
            )
            row = cursor.fetchone()

    if row is None:
        raise RuntimeError("persistence row was not readable after commit")

    result = PersistenceResult(
        genesis_id=genesis_id,
        relation_id=relation_id,
        loaded_genesis_id=row[0],
        loaded_relation_id=row[1],
    )
    if not result.persisted:
        raise RuntimeError(f"persistence identity mismatch: {result}")
    return result
