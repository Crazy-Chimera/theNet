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

    @staticmethod
    def _decode_genesis(payload: str) -> GenesisState:
        value = json.loads(payload)
        return GenesisState(
            id=value["id"],
            subject=value["subject"],
            created_at=value["created_at"],
            relations=tuple(value["relations"]),
            version=value["version"],
        )

    @staticmethod
    def _decode_relation(payload: str) -> Relation:
        value = json.loads(payload)
        return Relation(
            id=value["id"],
            source_id=value["source_id"],
            target_id=value["target_id"],
            kind=value["kind"],
            created_at=value["created_at"],
            version=value["version"],
        )

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
        return None if row is None else self._decode_genesis(row[0])

    def list_genesis(self) -> tuple[GenesisState, ...]:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT payload FROM genesis ORDER BY id")
            rows = cursor.fetchall()
        return tuple(self._decode_genesis(row[0]) for row in rows)

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
        return None if row is None else self._decode_relation(row[0])

    def list_relations(self) -> tuple[Relation, ...]:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT payload FROM relations ORDER BY id")
            rows = cursor.fetchall()
        return tuple(self._decode_relation(row[0]) for row in rows)

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PostgresStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
