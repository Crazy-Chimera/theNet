# Ω² Memory Contract

## Purpose

Ω² is the persistent memory primitive of theNet. It records an immutable reference to a state or event that has been selected for persistence.

Ω² stores identity and provenance; it does not itself decide truth, meaning, consensus, or relevance.

## Input

- `subject_id`: non-empty identifier being remembered
- `source_id`: non-empty identifier of the source event/state
- `created_at`: non-empty timestamp
- `kind`: non-empty memory classification

## Output

An immutable `MemoryRecord` containing the four inputs, a deterministic SHA-256 `id`, and `version=1`.

## Invariants

1. All inputs are non-empty strings.
2. Equal input produces equal memory identity.
3. Changing any input changes the identity.
4. The record is immutable.
5. Memory creation does not mutate its source.
6. No external service is required.
7. Ω² does not establish truth, verification, consensus, contribution, meaning, or convergence.

## Boundary

Ω records state transition. Ω² records a selected persistent reference to a state/event. Later ΦΩ² resonance may combine structural and memory identities.
