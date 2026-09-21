# Agent Ω State Contract

## Purpose

The Agent Ω state is the first integration boundary above the foundational layers. It binds one Genesis subject to one ΙΩΤΑ unity closure.

This is an integration primitive, not an autonomous agent. It does not yet propose, verify, learn, allocate resources, or change its own rules.

## Input

- `subject_id`: non-empty Genesis subject identifier.
- `singularity_id`: non-empty ΙΩΤΑ identifier.
- `created_at`: non-empty timestamp.

## Output

An immutable `AgentState`:

- `id`
- `subject_id`
- `singularity_id`
- `created_at`
- `version = 1`

## Identity

The state ID is SHA-256 over the canonical subject, singularity, timestamp, and version.

## Invariants

1. All defining values must be non-empty strings.
2. Same input produces the same state ID.
3. Changing any defining input changes the state ID.
4. The result is immutable.
5. Inputs are not mutated.
6. No external services are required.
7. AgentState does not mutate the referenced Genesis or ΙΩΤΑ state.
8. AgentState does not imply verification, consensus, contribution, learning, or autonomy.
9. The state is an integration boundary for later proposal → verification → convergence → commit cycles.

## Evolution Boundary

Future Agent Ω evolution should preserve the invariant:

`Identity(next) = f(Identity(current), verified_evolution)`

The function `f` is intentionally not implemented by this primitive.
