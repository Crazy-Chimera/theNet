# PostgresStore Contract

## Purpose

PostgresStore is the PostgreSQL implementation of the existing RuntimeStore persistence boundary.

It must preserve the same behavior as SQLiteStore without changing GenesisState or Relation.

## Interface

PostgresStore exposes exactly the RuntimeStore operations:

- save_genesis(state) -> None
- get_genesis(state_id) -> GenesisState | None
- save_relation(relation) -> None
- get_relation(relation_id) -> Relation | None
- close() -> None

## Invariants

1. Stored domain objects are returned with the same field values.
2. Saving the same object repeatedly is idempotent.
3. A storage conflict for an existing identifier with different content is rejected.
4. Reads of unknown identifiers return None.
5. PostgreSQL-specific connection and SQL details remain inside the adapter.
6. GenesisState and Relation remain unchanged.
7. The same backend contract tests can execute against SQLite and PostgreSQL.
8. Persistence is committed transactionally after successful writes.

## Serialization

The adapter stores canonical JSON payloads as text.

The database identifier is indexed as the primary key. The payload is not interpreted by the domain layer.

## Dependency

PostgreSQL support uses Psycopg 3. The dependency belongs to the storage/runtime layer, not to Genesis or Relation.

## Verification boundary

A live PostgreSQL instance is required for the PostgreSQL integration tests.

The test suite uses:

- SQLite as the always-available backend.
- PostgreSQL when THENET_POSTGRES_DSN is configured.

CI configures a PostgreSQL service and runs the same behavioral contract against both backends.