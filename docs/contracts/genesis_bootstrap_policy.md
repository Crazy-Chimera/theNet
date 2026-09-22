# Genesis Bootstrap Policy Contract

## Purpose

Expose the Genesis consensus boundary as an immutable policy object.

The policy separates population topology from later proposal execution. It answers only:

- how many independent non-proposer verifiers are eligible;
- what strict-majority quorum is required;
- whether collective learning is possible.

It does not validate truth, identity, Sybil resistance, or proposal content.

## Input

- `population_size`: positive integer

## Output

`GenesisBootstrapPolicy`:

- `population_size`
- `proposer_count = 1`
- `eligible_verifier_count = population_size - 1`
- `quorum`
- `collective_learning_possible`

## Rules

1. Population size must be a positive integer.
2. A single agent has zero independent verifiers.
3. A population of one cannot perform collectively verified learning.
4. For N >= 2, quorum is strict majority of N - 1 eligible verifiers.
5. Quorum is derived from population size; callers cannot override it.
6. The policy is immutable and deterministic.
7. The policy does not claim verifier independence beyond the Genesis simulation's explicit population boundary.

## Boundary

This is a bootstrap policy, not a general identity or trust system. Stronger verifier eligibility can be introduced later without changing the proposal or consensus primitives.
