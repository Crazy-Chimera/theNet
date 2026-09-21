# ΦΩ² Resonance Contract

## Purpose

ΦΩ² is the resonance layer of theNet. It connects relational structure (Φ) with persistent memory (Ω²) and produces a deterministic structural-memory coherence record.

ΦΩ² does not create new relations or mutate memory. It records which structural state and which memory state are being considered together.

## Input

- `structure_id`: non-empty Φ structure identifier
- `memory_id`: non-empty Ω² memory identifier
- `created_at`: non-empty timestamp

## Output

An immutable `Resonance` containing:
- `id`
- `structure_id`
- `memory_id`
- `created_at`
- `version = 1`

## Identity

The resonance identity is the SHA-256 hash of the canonical payload containing:
- version
- structure ID
- memory ID
- creation timestamp

The same inputs always produce the same resonance identity.

## Invariants

1. Structure and memory identifiers must be non-empty strings.
2. Timestamp must be a non-empty string.
3. Output is immutable.
4. Input values are not mutated.
5. Same input produces the same ID.
6. Changing structure or memory changes the ID.
7. Resonance is directional from structure state to memory state only in the sense of its typed fields; it does not infer causality.
8. ΦΩ² does not assert truth, quality, consensus, contribution, or convergence.
9. No external service is required.

## Boundary

- Φ describes relational structure.
- Ω² records a persistent memory reference.
- ΦΩ² records their co-presence as a resonance.
- Later layers may evaluate coherence, interpret meaning, or drive convergence.
