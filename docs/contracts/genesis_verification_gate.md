# Genesis Bootstrap Verification Gate Contract

## Purpose

The verification gate converts the bootstrap boundary into an explicit acceptance rule for the first collective proposal.

The gate answers only whether the bootstrap conditions permit independent verification. It does not score proposal quality or establish general consensus for later system states.

## Input

- `population_size`: positive integer.
- `verifier_count`: non-negative integer representing independent verifiers available to the proposer.
- `required_quorum`: positive integer when verification is required.

## Output

Immutable `GenesisVerificationGate` containing:

- `population_size`
- `verifier_count`
- `required_quorum`
- `approved`
- `reputation_required = false`
- `version = 1`

## Rules

1. The proposer is not an independent verifier.
2. A single-agent population cannot approve a collective proposal.
3. `verifier_count` cannot exceed `population_size - 1`.
4. `required_quorum` must be positive for this gate.
5. Approval requires `verifier_count >= required_quorum`.
6. The bootstrap gate does not require a higher reputation value `R`.
7. The gate is deterministic and immutable.
8. This gate does not evaluate proposal semantics, contribution quality, convergence, memory, or safety.

## Boundary

`GenesisBootstrapBoundary` describes what verification capacity exists.

`GenesisVerificationGate` determines whether that capacity satisfies the minimum bootstrap verification condition.

Later consensus layers may introduce stronger quorum rules, reputation weighting, challenge-response, or additional evidence without changing this bootstrap primitive.
