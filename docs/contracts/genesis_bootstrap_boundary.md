# Genesis Bootstrap Boundary Contract

## Purpose

Make the bootstrap limitation explicit: a proposer can exist alone, but collective learning requires at least one independent verifier.

## Inputs

- `population_size`: positive integer.

## Output

Immutable `GenesisBootstrapBoundary`:

- `population_size`
- `eligible_verifier_count = population_size - 1`
- `minimum_quorum`
- `collective_learning_possible`
- `reputation_required = false`

## Rules

1. A population of one has zero eligible independent verifiers.
2. A population of one cannot establish collective consensus under this bootstrap model.
3. For population >= 2, the minimum collective quorum is one verifier.
4. The bootstrap boundary does not require a higher reputation value (`R`) to establish the first collective verification.
5. Reputation may be introduced later as a weighting, trust, or resource-allocation signal; it is not a prerequisite of this bootstrap primitive.
6. The proposer is never counted as its own independent verifier.
7. The result is deterministic and immutable.

## Scope

This contract describes the current bootstrap architecture. It does not claim that all future consensus mechanisms must use the same quorum or reputation rules.
