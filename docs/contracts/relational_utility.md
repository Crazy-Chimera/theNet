# Verified Relational Utility Contract

## Purpose

Relational utility is the explicit, externally assessed signal that a contribution produced a useful effect on the relational structure.

TheNet does not infer usefulness from relation count or graph size. A utility value is accepted only as a supplied assessment with explicit evidence identifiers and a verification flag.

This keeps utility separate from Φ structure: Φ describes structure; relational utility describes assessed effect.

## Input

- `contributor_id`: non-empty string.
- `value`: finite number in [0, 1].
- `evidence_ids`: iterable of non-empty evidence identifiers.
- `verified`: boolean.
- `created_at`: non-empty string.

## Output

Immutable `RelationalUtility`:

- `id`
- `contributor_id`
- `value`
- `evidence_ids`: sorted unique tuple
- `verified`
- `created_at`
- `version=1`

## Invariants

1. The utility value is bounded to [0, 1].
2. `verified` must be boolean.
3. A verified utility record must contain at least one evidence identifier.
4. Evidence identifiers are canonicalized as sorted unique values.
5. The same valid input produces the same identity.
6. Changing the value, contributor, evidence, verification state, or timestamp changes the identity.
7. The output is immutable.
8. The primitive does not mutate relations, memory, resource state, or agent state.
9. Utility is an assessed signal, not proof of truth and not network consensus.
10. No external service is required.

## Architectural role

`relation → observed effect → evidence → verified relational utility → Ω-Credit`

The primitive deliberately does not decide whether evidence is truthful. Verification remains a separate boundary.
