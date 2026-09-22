# Genesis Population Simulation Contract

## Purpose

Provide a deterministic simulation harness for the first Agent Ω population. The harness tests whether proposal-driven evolution can proceed from explicit independent verifiers without requiring a higher reputation value.

## Input

- positive integer population size
- non-empty `created_at`
- proposal text

The verifier quorum is derived from the Genesis bootstrap policy and cannot be supplied by the caller.

## Process

1. Create one immutable Agent Ω state per population member.
2. The first agent creates a proposal against its current state.
3. Remaining agents create explicit verifications for that proposal.
4. Derive the strict-majority quorum from the number of eligible non-proposer verifiers.
5. If the derived quorum is reachable, only the proposer state evolves.
6. If no independent verifier exists, collective evolution is rejected.

## Invariants

1. Population members have distinct subject identities.
2. No reputation/higher-R value is required by the simulation.
3. Consensus is explicit and quorum-based.
4. For two agents, one independent verifier is sufficient under the bootstrap policy.
5. For three agents, two independent verifiers are required.
6. A single-agent population cannot collectively evolve.
7. Callers cannot override the bootstrap quorum.
8. Failed quorum does not mutate the source state.
9. Successful evolution creates a new immutable state version.
10. Verification remains distinct from reputation.

## Interpretation boundary

The simulation establishes only a protocol property: collective evolution can be gated by explicit verifier count without a higher-R mechanism. It does not establish that the bootstrap quorum is socially, economically, or epistemically sufficient in a real network.
