# Ω Process Contract

## Purpose

Ω represents a verified-compatible state transition: a compact immutable record that one system state has been replaced by another.

The module operationalizes the project language of Ω as **process / pohyb**. It records a transition; it does not itself decide whether the transition is useful, safe, meaningful, convergent, or correct.

## Input

- `from_state`: non-empty state identifier
- `to_state`: non-empty state identifier
- `reason`: non-empty transition reason
- `created_at`: non-empty transition timestamp

## Output

An immutable `OmegaTransition` containing:

- `id`: SHA-256 identity of the canonical transition
- `from_state`
- `to_state`
- `reason`
- `created_at`
- `version`: `1`

## Identity

The transition ID is deterministic over:

`created_at, from_state, reason, to_state, version`

The same transition input therefore produces the same ID.

## Invariants

1. All four input strings must be non-empty.
2. The output is immutable.
3. The same input produces the same transition ID.
4. Changing either state, reason, or timestamp changes the identity.
5. A transition may point from a state to itself; the module does not impose semantic rules on state change.
6. Input values are not mutated.
7. No external service or global state is required.
8. Ω does not establish verification, consensus, contribution, meaning, memory, convergence, or safety.
9. Ω records a state transition; later modules determine whether that transition may be committed.

## Integration boundary

Genesis creates initial states. Relation creates links. Φ describes structure. Ω records movement between state identifiers. Ω² later persists selected state/history, while verification and convergence remain separate concerns.
