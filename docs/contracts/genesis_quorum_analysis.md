# Genesis Quorum Analysis Contract

## Purpose

Provide a deterministic analysis of the Genesis population proposal path without changing consensus semantics.

The analysis makes the dependency on multiple entities explicit:

- one agent proposes;
- the proposer is excluded from verification;
- at most population_size - 1 verifier identities are available;
- a quorum q is reachable iff q <= population_size - 1.

This is an engineering simulation of the current runtime rules. It does not establish that a larger population is intrinsically more truthful or more secure.

## Input

- population_size: positive integer.
- max_quorum: positive integer.

## Output

An immutable GenesisQuorumAnalysis containing:

- population_size
- available_verifiers
- rows: ordered GenesisQuorumRow records for quorum values 1..max_quorum

Each row contains:

- quorum
- reachable
- required_population

required_population = quorum + 1.

## Invariants

1. population_size must be a positive integer.
2. max_quorum must be a positive integer.
3. available_verifiers = population_size - 1.
4. reachable iff quorum <= available_verifiers.
5. required_population = quorum + 1.
6. Row ordering is deterministic.
7. Output is immutable.
8. The analysis performs no proposal, verification, or state mutation.
9. The analysis does not treat identity count as Sybil resistance.
