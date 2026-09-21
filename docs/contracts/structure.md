# Φ Structure Contract

## Purpose

Φ is the structural layer of theNet. It describes the relational shape currently known without assigning meaning, contribution, verification, or convergence.

## Input

- `subject_ids`: iterable of non-empty strings.
- `relation_ids`: iterable of non-empty strings.

## Output

An immutable `Structure`:

- `id`
- `subject_ids`
- `relation_ids`
- `version = 1`

## Identity

The structure ID is SHA-256 over a canonical JSON representation of sorted unique subject and relation IDs plus the version.

Therefore equivalent sets produce the same structural identity regardless of input order or duplicate entries.

## Invariants

1. Every identifier is a non-empty string.
2. Empty collections are valid.
3. Duplicate identifiers are collapsed.
4. Input ordering does not affect identity.
5. The returned structure is immutable.
6. Inputs are not mutated.
7. No external services are required.
8. Φ does not imply verification, consensus, contribution, meaning, memory, convergence, or action.
9. A structure containing no subjects and no relations is a valid empty structural state.

## Boundary

- Genesis creates subjects.
- Relation creates directed links.
- Φ Structure composes those primitives into a structural snapshot.
- Later modules may interpret, verify, compare, persist, or evolve the structure.
