# Φ Structure Contract

## Purpose

Φ is the structural layer of theNet. It turns an entity reference and its explicit relation identifiers into a deterministic structural fingerprint without interpreting, verifying, or mutating the relations.

## Input

- `subject_id`: non-empty string.
- `relation_ids`: finite list or tuple of relation IDs; each ID must be a non-empty string.
- Relation identifiers are treated as a set for structural identity, so their order does not affect the result.

## Output

Immutable `PhiStructure`:

- `id`: SHA-256 identifier of the canonical structural payload.
- `subject_id`: subject represented by the structure.
- `relation_ids`: canonical sorted tuple of unique relation IDs.
- `version`: `1`.

## Invariants

1. Empty or non-string `subject_id` is rejected.
2. Empty, non-string, or invalid relation IDs are rejected.
3. Relation order does not change structural identity.
4. Duplicate relation IDs do not create duplicate structural edges.
5. Same canonical input produces the same `id`.
6. Different subject or relation membership produces a different `id`.
7. Output is immutable.
8. Φ does not resolve relation existence.
9. Φ does not imply verification, consensus, contribution, memory, convergence, meaning, or action.
10. No external services are required.

## Boundary

Genesis creates subjects. Relation creates explicit links. Φ represents the resulting local structure. Later layers may use the fingerprint for coherence, resonance, convergence, or memory.

## Verification

Tests cover construction, canonicalization, determinism, invalid input, immutability, and structural identity changes.
