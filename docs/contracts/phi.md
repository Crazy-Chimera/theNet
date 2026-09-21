# Φ Structure Contract

## Purpose

Φ is the first structural representation of a relation set. It derives a deterministic structural fingerprint from explicit relations without mutating the underlying entities or relations.

## Input

A finite iterable of relation objects. Each relation must expose:

- `id`
- `source_id`
- `target_id`
- `kind`

## Output

An immutable `PhiStructure` containing:

- `id`: SHA-256 fingerprint of the canonical relation structure
- `relation_ids`: sorted unique relation identifiers
- `node_ids`: sorted unique subject identifiers appearing in the relations
- `version`: `1`

## Invariants

1. The input relation collection is not mutated.
2. Relation ordering does not affect the resulting structure ID.
3. Repeated relation IDs are represented once.
4. The same structural input produces the same ID.
5. Changing a relation identifier changes the structure ID.
6. Changing a relation endpoint or kind changes the structure ID when the corresponding relation ID changes.
7. An empty relation collection is valid and produces an empty structural state.
8. The output is immutable.
9. Φ does not verify relations, establish consensus, infer meaning, allocate resources, or mutate memory.
10. No external service is required.

## Boundary

Genesis creates subjects. Relation creates directed links. Φ represents the resulting relational structure. Verification, convergence, meaning, memory, expression, self-knowledge and co-definition remain later concerns.
