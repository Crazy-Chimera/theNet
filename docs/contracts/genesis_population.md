# Genesis Population Simulation Contract

## Purpose

Provide a deterministic simulation harness for the first Agent Ω population. The harness tests whether proposal-driven evolution can proceed with an explicit verifier quorum without requiring a higher reputation value or an implicit majority rule.

## Input

- positive integer population size
- positive integer quorum
- non-empty created_at
- proposal text

## Process

1. Create one immutable Agent Ω state per population member.
2. The first agent creates a proposal against its current state.
3. Remaining agents independently create valid verifications for that proposal.
4. The configured quorum is passed to collective evolution.
5. If enough distinct verifiers exist, only the proposer state evolves.
6. If the quorum exceeds the number of available distinct verifiers, evolution is rejected.

## Invariants

1. Population members have distinct subject identities.
2. No reputation/higher-R value is required by the simulation.
3. Consensus is explicit and quorum-based.
4. A quorum of one permits one verifier.
5. A quorum of two requires two distinct verifiers.
6. A quorum larger than the available verifier population cannot be reached.
7. Failed quorum does not mutate the source state.
8. Successful evolution creates a new immutable state version.
9. Verification remains distinct from reputation.

## Interpretation boundary

The simulation establishes only a protocol property: collective evolution can be gated by explicit verifier count without a higher-R mechanism. It does not establish that a particular quorum is socially, economically, or epistemically sufficient in a real network.
