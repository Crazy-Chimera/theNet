# Genesis Majority Learning Contract

## Purpose

Provide a policy-bound facade for repeated Genesis learning using the strict-majority quorum of the independent, non-proposer population.

The facade keeps the existing learning engine explicit: it derives the quorum once and delegates to `simulate_genesis_learning`.

## Rule

For population size N:

`eligible_verifiers = N - 1`

`quorum = floor(eligible_verifiers / 2) + 1`

Population size 1 is rejected because no independent verifier exists.

## Invariants

1. No reputation or higher-R value is consulted.
2. The proposer is excluded from verification.
3. The derived quorum is deterministic.
4. The underlying learning semantics remain unchanged.
5. A failed quorum cannot evolve the proposer.
6. The facade does not claim that majority identity count provides Sybil resistance or truth.

## Boundary

`genesis_majority_quorum` defines policy.
`simulate_genesis_learning` executes the learning simulation.
This facade composes the two without changing either primitive.
