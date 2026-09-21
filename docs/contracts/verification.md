# Verification Contract

## Purpose

Verification evaluates a Proposal against explicit evidence without turning a single verification result into consensus or commit.

## Input

- `proposal_id`: non-empty proposal identifier.
- `verifier_id`: non-empty verifier identifier.
- `evidence`: non-empty evidence digest or canonical evidence reference.
- `valid`: boolean verification result.
- `created_at`: non-empty timestamp.

## Output

An immutable `Verification` containing:

- `id`: deterministic SHA-256 identity.
- `proposal_id`
- `verifier_id`
- `evidence`
- `valid`
- `created_at`
- `version = 1`

## Invariants

1. Defining identifiers, evidence, and timestamp are non-empty strings.
2. `valid` must be boolean.
3. Same input produces the same verification ID.
4. Changing any defining input changes the ID.
5. The result is immutable.
6. Inputs are not mutated.
7. Verification does not mutate the proposal or base state.
8. One verification is one verifier's claim; it is not consensus.
9. Verification does not itself commit state or create learning.
10. No external service is required.

## Evolution Boundary

`state -> proposal -> verification -> consensus/convergence -> commit -> memory`

The separation keeps evidence assessment distinct from collective agreement.
