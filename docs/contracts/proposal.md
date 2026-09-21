# Proposal Contract

## Purpose

A Proposal is a candidate change submitted against a known Agent Ω state. It is the first explicit unit of evolutionary intent above the immutable state primitives.

A proposal is not a change. It is not evidence of correctness, consensus, or contribution.

## Input

- `proposer_id`: non-empty agent identifier.
- `base_state_id`: non-empty state identifier the proposal is based on.
- `proposal`: non-empty canonical proposal description.
- `created_at`: non-empty timestamp.

## Output

An immutable `Proposal`:

- `id`
- `proposer_id`
- `base_state_id`
- `proposal`
- `created_at`
- `version = 1`

## Identity

The ID is SHA-256 over the canonical proposer, base state, proposal, timestamp, and version.

## Invariants

1. All defining values must be non-empty strings.
2. Same input produces the same proposal ID.
3. Changing any defining input changes the ID.
4. The result is immutable.
5. Inputs are not mutated.
6. No external services are required.
7. Creating a proposal does not mutate the base state.
8. A proposal does not establish validity, consensus, contribution, or learning by itself.
9. Verification must be a separate step.
10. A future commit may change state only after the proposal passes the required verification policy.

## Evolution Boundary

`state -> proposal -> verification -> convergence -> commit -> memory`

This separation prevents intent from being confused with verified evolution.
