# ΦΩ² Resonance Contract

## Purpose

ΦΩ² is the resonance boundary between relational structure (Φ) and persistent memory (Ω²). It records that a particular structural snapshot and a particular memory record are being considered together at a defined structural observation point.

The primitive is intentionally referential: it links existing identities rather than copying or mutating their contents.

## Input

- `structure_id`: non-empty string identifying a Φ structural snapshot.
- `memory_id`: non-empty string identifying an Ω² memory record.
- `created_at`: non-empty string identifying the resonance observation point.

## Output

Immutable `Resonance`:

- `id`: SHA-256 identity of the canonical resonance payload.
- `structure_id`
- `memory_id`
- `created_at`
- `version=1`

## Identity

The identity is SHA-256 over canonical JSON containing:

- `created_at`
- `memory_id`
- `structure_id`
- `version=1`

The canonical representation is deterministic and key-order independent.

## Invariants

1. All required fields must be non-empty strings.
2. Same valid input produces the same resonance identity.
3. Changing the structure reference changes identity.
4. Changing the memory reference changes identity.
5. Changing the observation timestamp changes identity.
6. Output is immutable.
7. Input values are not mutated.
8. Resonance does not mutate Φ or Ω².
9. Resonance does not itself establish verification, consensus, truth, meaning, contribution, or convergence.
10. No external service is required.

## Boundary

- Φ describes relational structure.
- Ω² retains a memory reference to state evolution.
- ΦΩ² binds the two references into a deterministic resonance record.
- Γ convergence and later layers may consume resonance; they remain responsible for their own semantics and verification.

## Required tests

- creation
- deterministic identity
- required-field rejection
- immutability
- structure-reference change
- memory-reference change
- timestamp change
- integration with real Φ and Ω² primitives
