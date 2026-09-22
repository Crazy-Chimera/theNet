# Φ Structure — Contract

## Purpose

Φ is the structural layer of theNet. It represents a deterministic, immutable structural fingerprint of an ordered set of relation identifiers without interpreting, verifying, scoring, or mutating those relations.

## Input

- `relation_ids`: a sequence of non-empty strings.
- The sequence order is significant.
- An empty sequence is valid and represents an empty structure.

## Output

An immutable `PhiStructure` containing:

- `id`: SHA-256 identifier of the canonical structure.
- `relation_ids`: the exact ordered tuple supplied by the caller.
- `version`: `1`.

## Identity

The identifier is derived from the canonical JSON representation of:

`{relation_ids, version}`

with sorted object keys and compact separators.

Therefore the same ordered input produces the same identifier.

## Invariants

1. `relation_ids` must be a sequence.
2. Every relation identifier must be a non-empty string.
3. The returned structure is immutable.
4. Input order is preserved.
5. Reordering identifiers changes the identity.
6. Adding or removing an identifier changes the identity.
7. The empty structure is valid and deterministic.
8. The function does not mutate supplied input.
9. No external services are required.
10. Φ describes structure only; it does not establish truth, consensus, contribution, memory, convergence, meaning, or safety.

## Boundary

- Genesis creates subjects.
- Relation creates directed links.
- Φ Structure composes relation identifiers into a structural state.
- Later layers may use this structure for coherence, resonance, convergence, memory, or contribution calculations.

## Required tests

- empty structure
- ordered structure creation
- deterministic identity
- order sensitivity
- addition/removal sensitivity
- invalid container rejection
- invalid relation identifier rejection
- immutability
- input preservation
