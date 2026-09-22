# Genesis Learning Simulation Contract

## Purpose

Model repeated proposal-driven learning for the first Agent Omega population.

The simulation is deliberately narrow: it asks whether an agent can advance through successive verified proposals when reputation (R) is not an input and when each step is gated only by an explicit verifier quorum.

## Input

- a deterministic Genesis population
- a non-empty ordered sequence of proposal texts
- a positive quorum
- a deterministic creation timestamp sequence

## Process

For each proposal in order:

1. the current proposer state creates a proposal;
2. the other population members create independent valid verifications;
3. collective consensus evaluates the configured quorum;
4. if quorum is reachable, the proposer evolves to a new immutable state;
5. if quorum is unreachable, the step remains uncommitted and later steps are not applied.

## Output

An immutable GenesisLearningRun containing:

- the original population;
- one GenesisLearningStep per attempted proposal;
- the final proposer state.

Each step records:

- proposal;
- verifier count;
- quorum;
- whether consensus was reached;
- whether evolution occurred;
- resulting state version.

## Invariants

1. Reputation (R) is not required or consulted.
2. A proposer cannot verify its own proposal.
3. Each verifier contributes at most one verification to consensus.
4. A quorum is reachable only when population size minus one is at least the configured quorum.
5. Successful learning increments the proposer state version by one.
6. Failed quorum does not mutate the current proposer state.
7. Learning is sequential: a failed step stops the run.
8. The same inputs produce the same output.
9. The simulation does not claim that verifier count alone provides Sybil resistance or epistemic truth.
10. No external service is required.

## Interpretation

The simulation can establish protocol feasibility under explicit assumptions. It cannot establish that a given quorum is sufficient for real-world truth, safety, or decentralized identity.

The experiment distinguishes two separate questions:

- Can learning occur without higher R? Yes, if the configured quorum is reachable.
- Can learning occur with no independent verifier? No under this protocol, because the proposer is excluded from self-verification and quorum must be at least one.
