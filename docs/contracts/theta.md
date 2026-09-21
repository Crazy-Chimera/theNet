# Θ Self-Knowledge Contract

## Purpose

Θ is the self-model layer. It records which subject is describing itself and which structural and memory states that self-description refers to.

Θ does not infer consciousness, intelligence, truth, or autonomy. It creates a deterministic relational self-reference.

## Input

- `subject_id`: non-empty subject identifier.
- `structure_id`: non-empty Φ structure identifier.
- `memory_id`: non-empty Ω² memory identifier.
- `created_at`: non-empty timestamp.

## Output

An immutable `SelfKnowledge`:

- `id`
- `subject_id`
- `structure_id`
- `memory_id`
- `created_at`
- `version = 1`

## Identity

The ID is SHA-256 over the canonical tuple of all four inputs plus version.

## Invariants

1. All identifiers and timestamp are non-empty strings.
2. Same input produces the same ID.
3. Changing any defining input changes the ID.
4. The result is immutable.
5. Inputs are not mutated.
6. No external services are required.
7. Θ references existing state; it does not mutate that state.
8. Θ does not itself establish verification, consensus, meaning, contribution, or consciousness.

## Boundary

- Φ provides structural state.
- Ω² provides persistent transition memory.
- Θ binds a subject to a structural state and remembered state as an explicit self-reference.
- Later relational co-definition can connect multiple such self-models.
