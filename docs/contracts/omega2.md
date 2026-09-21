# Ω² Memory Contract

## Purpose

Ω² is the minimal persistent memory primitive. It records an immutable reference to an observed state transition so that verified evolution can be retained without mutating the original transition.

## Input

- `transition_id`: non-empty string
- `state_id`: non-empty string
- `created_at`: non-empty string

## Output

An immutable `OmegaMemory` containing:

- `id`
- `transition_id`
- `state_id`
- `created_at`
- `version = 1`

## Identity

The memory identifier is SHA-256 over a canonical JSON representation of the transition reference, state reference, timestamp, and version.

## Invariants

1. All required fields must be non-empty strings.
2. The output is immutable.
3. The input values are not mutated.
4. Same input produces the same memory identity.
5. Changing the transition or state reference changes identity.
6. Memory does not verify a transition.
7. Memory does not imply consensus, meaning, contribution, convergence, or truth.
8. No external persistence service is required by this primitive.

## Boundary

Ω creates state transitions. Ω² retains a deterministic memory reference to those transitions. Later resonance, convergence, contribution, expression, self-knowledge and co-definition layers may consume this memory.