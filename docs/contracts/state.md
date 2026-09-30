# State / Observe Contract

## Purpose

State is the local immutable snapshot derived directly from an existing
UserFlow. Observe reads that snapshot without changing it.

The intended local path is:

UserFlow → State → Observe

No distributed infrastructure is required.

## State

### Input

An existing immutable UserFlow.

### Output

Immutable State containing:

- id
- flow_id
- context_id
- subject_id
- stage
- ordered relation_ids
- version=1

The State identity is SHA-256 over the complete state-defining projection of
the UserFlow.

## Observation

Observe returns an immutable Observation containing the state identity and a
small descriptive projection:

- state_id
- flow_id
- subject_id
- stage
- relation_count
- relation_ids
- version=1

Observation is read-only and deterministic.

## Invariants

1. State accepts only UserFlow.
2. State does not mutate the UserFlow or its RequestContext.
3. Relation order is preserved.
4. Equal UserFlow input produces equal State identity.
5. Different flow state produces a different State identity.
6. Observe does not mutate State.
7. Observe is deterministic for the same State.
8. No network, database, consensus, clock, or external service is required.
9. State does not claim that a relation is true, trusted, verified, meaningful,
   globally agreed, or convergent.

## Boundary

UserFlow owns local request evolution.
State materializes the current flow as a stable snapshot.
Observe reads that snapshot.

Later layers may interpret, propose, verify, converge, remember, or express
the observation without changing these primitives.
