"""SQLite implementation of theNet's RuntimeStore contract."""

from __future__ import annotations

from pathlib import Path
import json
import sqlite3

from src.genesis import GenesisState
from src.relation import Relation


class SQLiteStore:
    """Small transactional store that preserves domain objects unchanged."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(str(path))
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS genesis (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );
            """
        )
        self._connection.commit()

    @staticmethod
    def _encode(value: object) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    def _save(self, table: str, identifier: str, payload: str) -> None:
        existing = self._connection.execute(
            f"SELECT payload FROM {table} WHERE id = ?",
            (identifier,),
        ).fetchone()

        if existing is None:
            self._connection.execute(
                f"INSERT INTO {table} (id, payload) VALUES (?, ?)",
                (identifier, payload),
            )
            self._connection.commit()
            return

        if existing[0] != payload:
            raise ValueError("storage conflict: identifier already contains different data")

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
        row = self._connection.execute(
            "SELECT payload FROM genesis WHERE id = ?",
            (state_id,),
        ).fetchone()
        return None if row is None else self._decode_genesis(row[0])

    def list_genesis(self) -> tuple[GenesisState, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM genesis ORDER BY id"
        ).fetchall()
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
        row = self._connection.execute(
            "SELECT payload FROM relations WHERE id = ?",
            (relation_id,),
        ).fetchone()
        return None if row is None else self._decode_relation(row[0])

    def list_relations(self) -> tuple[Relation, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM relations ORDER BY id"
        ).fetchall()
        return tuple(self._decode_relation(row[0]) for row in rows)

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
