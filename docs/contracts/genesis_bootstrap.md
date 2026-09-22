# Genesis Bootstrap Consensus Boundary

## Purpose

Define the minimum conditions under which the first Agent Ω population can perform proposal-driven collective learning.

The bootstrap boundary separates two questions:

1. Can an agent generate a proposal?
2. Can the population collectively authorize evolution of that proposal?

The first does not require a verifier. The second does.

## Policy

For a population of N agents:

- proposer = one agent
- eligible verifier count = N - 1
- strict-majority quorum = floor((N - 1) / 2) + 1
- N = 1 has no independent verifier and cannot perform collectively verified learning.
- N >= 2 can reach a positive quorum under the majority policy.

Examples:

| Population | Independent verifiers | Majority quorum |
|---:|---:|---:|
| 1 | 0 | impossible |
| 2 | 1 | 1 |
| 3 | 2 | 2 |
| 4 | 3 | 2 |
| 5 | 4 | 3 |

## Higher recursive depth

A higher recursive depth R is not a substitute for an independent verifier in the current model.

R may increase the depth or expressiveness of an agent's internal reasoning, but the consensus rule depends on independent verifier records. Therefore:

`higher R != additional verifier`

and

`self-verification != independent consensus`.

## Security boundary

Population count alone does not establish Sybil resistance, truth, or independence in the real world.

The current Genesis simulation treats the non-proposer population members as eligible verifiers. A future trust/identity layer may constrain eligibility using stronger independence evidence.

## Required behavior

1. Single-agent Genesis can propose but cannot reach collective consensus.
2. Two-agent Genesis can reach quorum with the one non-proposer verifier.
3. Three-agent Genesis requires both non-proposer verifiers.
4. Failed quorum leaves the proposer state unchanged.
5. Reached quorum permits evolution.
6. Majority learning must derive its quorum from population size rather than from an externally supplied arbitrary value.
