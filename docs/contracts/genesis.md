# Genesis Module Contract

## Purpose

Genesis is the minimal entry point for creating the initial system state.

The module establishes a deterministic origin without introducing later architectural layers prematurely.

## Contract

### Input

A Genesis request contains:

- `subject`: non-empty stable identifier of the initial entity.
- `createdAt`: non-empty canonical timestamp supplied by the caller.

### Output

A Genesis state contains:

- `id`: deterministic identifier derived from the canonical Genesis content.
- `subject`: the original subject identifier.
- `createdAt`: the original timestamp.
- `relations`: an empty immutable relation collection.
- `version`: `1`.

### Invariants

1. Empty subject is rejected.
2. Empty timestamp is rejected.
3. The initial relation collection is empty.
4. The same valid input produces the same state identifier.
5. Genesis creation does not mutate its input.
6. Genesis does not depend on external services.
7. Genesis does not create contribution, memory, convergence, or identity history by itself.

## Verification

Tests must cover:

- valid creation,
- deterministic identity,
- empty subject,
- empty timestamp,
- input immutability,
- output immutability,
- empty initial relations.

## Integration Boundary

Genesis is intentionally independent of Relation and all later modules.

Later modules may consume Genesis state, but Genesis must not import or depend on them.
