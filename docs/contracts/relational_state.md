# Relational State Contract

## Purpose

Relational State is the first derived state after Genesis + Relation.

It represents the current structural state of one subject as a deterministic snapshot of its known relations. It does not mutate Relation objects and does not assign meaning, contribution, verification, consensus, or memory.

## Input

- `subject_id`: non-empty string.
- `relations`: finite collection of Relation objects belonging to the subject.
- A relation belongs to the subject when `source_id == subject_id` or `target_id == subject_id`.

## Output

Immutable `RelationalState`:

- `id`: deterministic SHA-256 identity of the canonical state.
- `subject_id`
- `relation_ids`: canonical, deduplicated, sorted tuple.
- `relation_count`
- `version = 1`

## Invariants

1. Empty subject identifiers are rejected.
2. Every input item must be a Relation.
3. Relations unrelated to the subject are rejected rather than silently discarded.
4. Duplicate relations do not create duplicate state entries.
5. Relation order in the input does not affect state identity.
6. The same subject and relation set produce the same state ID.
7. Changing the relation set changes the state ID.
8. The returned state is immutable.
9. Input collections are not mutated.
10. Relational State is a snapshot; creating it does not mutate Genesis or Relation objects.
11. No external services are required.
12. The state does not imply verification, consensus, contribution, meaning, convergence, or memory.

## Canonical identity

The state identity is SHA-256 over canonical JSON containing:

- `subject_id`
- sorted unique `relation_ids`
- `version = 1`

## Boundary

Genesis creates an entity.

Relation creates an explicit directed link.

Relational State derives the subject's structural relation snapshot.

Later Φ Structure may derive richer structural properties from this state.
