# Genesis Majority Quorum Contract

## Purpose

Define the default strict-majority quorum policy for the first Agent Ω population without changing the underlying Consensus primitive.

The proposer is excluded from the verifier population. A strict majority therefore applies to the remaining independent verifiers.

## Rule

For population size N:

- eligible verifiers = N - 1
- majority quorum = floor((N - 1) / 2) + 1

This means:

- N = 1 -> no verifier exists; learning cannot be collectively verified.
- N = 2 -> 1 independent verifier is sufficient for a strict majority of eligible verifiers.
- N = 3 -> 2 independent verifiers are required.
- N = 4 -> 2 independent verifiers are required.

## Invariants

1. Population size must be a positive integer.
2. The proposer is never counted as its own verifier.
3. Population size 1 cannot produce a positive quorum.
4. The returned quorum is deterministic.
5. This is a policy helper; it does not weaken Consensus.
6. Higher recursive depth R does not substitute for an independent verifier in this model.

## Boundary

Consensus decides whether the declared quorum was reached. This helper only derives a default quorum from population size.
