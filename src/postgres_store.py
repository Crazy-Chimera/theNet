"""PostgreSQL implementation of theNet's RuntimeStore contract."""

from __future__ import annotations

from pathlib import Path
import json

import psycopg

from src.genesis import GenesisState
from src.relation import Relation


class PostgresStore:
    """Transactional PostgreSQL store that preserves domain objects unchanged."""

    def __init__(self, dsn: str | Path) -> None:
        self._connection = psycopg.connect(str(dsn))
        self._initialize()

    def _initialize(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS genesis (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS relations (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
        self._connection.commit()

    @staticmethod
    def _encode(value: object) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    def _save(self, table: str, identifier: str, payload: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT payload FROM {table} WHERE id = %s",
                (identifier,),
            )
            existing = cursor.fetchone()

            if existing is None:
                cursor.execute(
                    f"INSERT INTO {table} (id, payload) VALUES (%s, %s)",
                    (identifier, payload),
                )
                self._connection.commit()
                return

            if existing[0] != payload:
                self._connection.rollback()
                raise ValueError(
                    "storage conflict: identifier already contains different data"
                )

        self._connection.commit()

    def save_genesis(self, state: GenesisState) -> None:
        payload = self._encode(
            {
                "id": state.id,
                "subject": state.subject,
                "created_at": state.created_at,
                "relations": list(state.relations),
                "version": state.version,
            }
        )
        self._save("genesis", state.id, payload)

    def get_genesis(self, state_id: str) -> GenesisState | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM genesis WHERE id = %s",
                (state_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        value = json.loads(row[0])
        return GenesisState(
            id=value["id"],
            subject=value["subject"],
            created_at=value["created_at"],
            relations=tuple(value["relations"]),
            version=value["version"],
        )

    def save_relation(self, relation: Relation) -> None:
        payload = self._encode(
            {
                "id": relation.id,
                "source_id": relation.source_id,
                "target_id": relation.target_id,
                "kind": relation.kind,
                "created_at": relation.created_at,
                "version": relation.version,
            }
        )
        self._save("relations", relation.id, payload)

    def get_relation(self, relation_id: str) -> Relation | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM relations WHERE id = %s",
                (relation_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        value = json.loads(row[0])
        return Relation(
            id=value["id"],
            source_id=value["source_id"],
            target_id=value["target_id"],
            kind=value["kind"],
            created_at=value["created_at"],
            version=value["version"],
        )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PostgresStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
