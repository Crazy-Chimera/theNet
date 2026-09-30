"""SQLite-backed episodic, semantic, and procedural memory for theNet."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3


def _id(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class EpisodicMemory:
    id: str
    subject_id: str
    source_id: str
    content: str
    created_at: str
    version: int = 1


@dataclass(frozen=True)
class SemanticMemory:
    id: str
    subject_id: str
    pattern: str
    confidence: float
    created_at: str
    version: int = 1


@dataclass(frozen=True)
class ProceduralSkill:
    id: str
    subject_id: str
    skill: str
    success_count: int
    failure_count: int
    created_at: str
    version: int = 1


def create_episodic_memory(
    subject_id: str,
    source_id: str,
    content: str,
    created_at: str,
) -> EpisodicMemory:
    for name, value in {
        "subject_id": subject_id,
        "source_id": source_id,
        "content": content,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    return EpisodicMemory(
        id=_id(
            {
                "created_at": created_at,
                "content": content,
                "source_id": source_id,
                "subject_id": subject_id,
                "version": 1,
            }
        ),
        subject_id=subject_id,
        source_id=source_id,
        content=content,
        created_at=created_at,
    )


def create_semantic_memory(
    subject_id: str,
    pattern: str,
    confidence: float,
    created_at: str,
) -> SemanticMemory:
    for name, value in {
        "subject_id": subject_id,
        "pattern": pattern,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise ValueError("confidence must be numeric")
    if not 0.0 <= float(confidence) <= 1.0:
        raise ValueError("confidence must be between 0 and 1")

    return SemanticMemory(
        id=_id(
            {
                "created_at": created_at,
                "pattern": pattern,
                "subject_id": subject_id,
                "version": 1,
            }
        ),
        subject_id=subject_id,
        pattern=pattern,
        confidence=float(confidence),
        created_at=created_at,
    )


def create_procedural_skill(
    subject_id: str,
    skill: str,
    created_at: str,
) -> ProceduralSkill:
    for name, value in {
        "subject_id": subject_id,
        "skill": skill,
        "created_at": created_at,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be non-empty")

    return ProceduralSkill(
        id=_id(
            {
                "skill": skill,
                "subject_id": subject_id,
                "version": 1,
            }
        ),
        subject_id=subject_id,
        skill=skill,
        success_count=0,
        failure_count=0,
        created_at=created_at,
    )


class SQLiteMemoryStore:
    """Transactional local memory store with three explicit memory classes."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(str(path), check_same_thread=False)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS semantic_memory (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS procedural_memory (
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
        row = self._connection.execute(
            f"SELECT payload FROM {table} WHERE id = ?",
            (identifier,),
        ).fetchone()
        if row is None:
            self._connection.execute(
                f"INSERT INTO {table} (id, payload) VALUES (?, ?)",
                (identifier, payload),
            )
            self._connection.commit()
            return
        if row[0] != payload:
            raise ValueError("memory conflict: identifier already contains different data")

    def save_episodic(self, memory: EpisodicMemory) -> None:
        payload = self._encode(memory.__dict__)
        self._save("episodic_memory", memory.id, payload)

    def get_episodic(self, memory_id: str) -> EpisodicMemory | None:
        row = self._connection.execute(
            "SELECT payload FROM episodic_memory WHERE id = ?",
            (memory_id,),
        ).fetchone()
        if row is None:
            return None
        value = json.loads(row[0])
        return EpisodicMemory(**value)

    def list_episodic(self) -> tuple[EpisodicMemory, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM episodic_memory ORDER BY id"
        ).fetchall()
        return tuple(EpisodicMemory(**json.loads(row[0])) for row in rows)

    def save_semantic(self, memory: SemanticMemory) -> None:
        payload = self._encode(memory.__dict__)
        self._save("semantic_memory", memory.id, payload)

    def get_semantic(self, memory_id: str) -> SemanticMemory | None:
        row = self._connection.execute(
            "SELECT payload FROM semantic_memory WHERE id = ?",
            (memory_id,),
        ).fetchone()
        if row is None:
            return None
        return SemanticMemory(**json.loads(row[0]))

    def list_semantic(self) -> tuple[SemanticMemory, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM semantic_memory ORDER BY id"
        ).fetchall()
        return tuple(SemanticMemory(**json.loads(row[0])) for row in rows)

    def save_procedural(self, skill: ProceduralSkill) -> None:
        payload = self._encode(skill.__dict__)
        self._save("procedural_memory", skill.id, payload)

    def get_procedural(self, skill_id: str) -> ProceduralSkill | None:
        row = self._connection.execute(
            "SELECT payload FROM procedural_memory WHERE id = ?",
            (skill_id,),
        ).fetchone()
        if row is None:
            return None
        return ProceduralSkill(**json.loads(row[0]))

    def update_procedural(
        self,
        skill_id: str,
        *,
        success: bool,
    ) -> ProceduralSkill:
        skill = self.get_procedural(skill_id)
        if skill is None:
            raise KeyError(skill_id)
        if not isinstance(success, bool):
            raise ValueError("success must be boolean")

        updated = ProceduralSkill(
            id=skill.id,
            subject_id=skill.subject_id,
            skill=skill.skill,
            success_count=skill.success_count + int(success),
            failure_count=skill.failure_count + int(not success),
            created_at=skill.created_at,
            version=skill.version + 1,
        )
        payload = self._encode(updated.__dict__)
        self._connection.execute(
            "UPDATE procedural_memory SET payload = ? WHERE id = ?",
            (payload, skill.id),
        )
        self._connection.commit()
        return updated

    def list_procedural(self) -> tuple[ProceduralSkill, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM procedural_memory ORDER BY id"
        ).fetchall()
        return tuple(ProceduralSkill(**json.loads(row[0])) for row in rows)

    def table_names(self) -> tuple[str, ...]:
        rows = self._connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name IN (
                'episodic_memory',
                'semantic_memory',
                'procedural_memory'
            )
            ORDER BY name
            """
        ).fetchall()
        return tuple(row[0] for row in rows)

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteMemoryStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


__all__ = [
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralSkill",
    "SQLiteMemoryStore",
    "create_episodic_memory",
    "create_semantic_memory",
    "create_procedural_skill",
]
