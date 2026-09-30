# RuntimeStore Contract

## Purpose

`RuntimeStore` is the persistence boundary between theNet domain objects and a concrete storage backend.

The storage layer must not redefine or mutate the domain contracts for `GenesisState` or `Relation`.

## Interface

The runtime store exposes:

- `save_genesis(state) -> None`
- `get_genesis(state_id) -> GenesisState | None`
- `save_relation(relation) -> None`
- `get_relation(relation_id) -> Relation | None`
- `close() -> None`

## Invariants

1. Stored domain objects are returned with the same field values.
2. Saving the same object repeatedly is idempotent.
3. A storage conflict for an existing identifier with different content is rejected.
4. Reads of unknown identifiers return `None`.
5. Storage implementation details do not leak into Genesis or Relation.
6. No backend-specific type becomes part of the domain model.
7. The interface supports replacing SQLite with PostgreSQL without changing domain contracts.
8. Concrete stores own persistence concerns only: serialization, indexing, transactions, and connection lifecycle.

## Backend progression

Current backend:

`RuntimeStore -> SQLiteStore`

Prepared backend:

`RuntimeStore -> PostgresStore`

PostgreSQL is intentionally not introduced as a runtime dependency at this stage. The contract is backend-neutral so the later PostgreSQL adapter can reuse the same domain and storage tests.