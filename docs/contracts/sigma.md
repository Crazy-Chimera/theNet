# Σ Essence Contract

## Purpose

Σ is the essence/ground abstraction. The source framework defines Σ as the ground of all relations: not a node or an additional relation, but the potential in which relations exist.

For theNet, this is represented operationally as an immutable canonical ground state derived from the relation context. This implementation is a software abstraction; it does not assert the source document's physical or quantum claims as established science.

## Input

- `relation_ids`: iterable of relation identifiers.
- Identifiers must be non-empty strings.

## Output

An immutable `Essence`:

- `id`
- `relation_ids`
- `version = 1`

## Identity

The ID is SHA-256 over canonical JSON containing the sorted unique relation identifiers and version.

The same relational ground therefore has the same deterministic identity independent of input ordering.

## Invariants

1. Every relation identifier must be a non-empty string.
2. Empty relation context is valid as a neutral ground state.
3. Duplicate relation identifiers are collapsed.
4. Input ordering does not change identity.
5. The result is immutable.
6. Input collections are not mutated.
7. No external services are required.
8. Σ does not assert truth, consensus, meaning, or consciousness.
9. Σ does not mutate the relations from which it is derived.
10. The implementation must remain an explicit software abstraction of the source framework.

## Boundary

- Ρ describes relational co-definition.
- Σ represents the operational ground of the resulting relation context.
- ΙΩΤΑ may later integrate Σ with the other layers into a unified state.
