# State Contract

## Purpose

State is the local, immutable snapshot produced from a UserFlow after Relation.
It represents what the local agent currently holds as state without introducing
distributed consensus, persistence, or external infrastructure.

## Input

A UserFlow is represented by:

- `flow_id`: non-empty string
- `subject_id`: non-empty string
- `events`: ordered tuple of non-empty string event identifiers

## Output

An immutable State:

- `id`
- `flow_id`
- `subject_id`
- `events`
- `version = 1`

And a pure observation:

- `state_id`
- `flow_id`
- `subject_id`
- `event_count`
- `events`
- `version`

## Identity

State identity is SHA-256 over the canonical representation of all
state-defining fields. Equal UserFlow input MUST produce equal State identity.

## Invariants

1. `flow_id` and `subject_id` must be non-empty strings.
2. Events must be an ordered immutable sequence.
3. Empty events are allowed: a flow can exist before its first event.
4. State is immutable after creation.
5. Event order is significant.
6. Different state-defining input produces a different state identity.
7. Observation does not mutate State.
8. Observation is deterministic for the same State.
9. No network, database, consensus, clock, or external service is required.
10. State does not imply truth, verification, contribution, convergence, or meaning.

## Boundary

`UserFlow → State → Observe`

- UserFlow supplies local ordered experience.
- State materializes that experience as a stable snapshot.
- Observe reads the snapshot without changing it.

Later layers may interpret, verify, converge, remember, or commit the
observation. They must not be smuggled into State itself.
