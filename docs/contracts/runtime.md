# Agent Ω MVP Runtime Contract

## Purpose

The runtime facade composes the already-tested immutable primitives into one executable learning cycle. It is orchestration only: domain decisions remain explicit inputs to the underlying primitives.

## Operations

### build_closure

Inputs:

- source subject
- target subject
- relation kind
- proposal text
- verifier evidence
- expression identifier
- creation timestamp

Produces a GenesisClosure containing the complete Φ → ΙΩΤΑ chain.

### advance

Inputs:

- current AgentState
- a verified Proposal
- a Verification
- a converged EvolutionCommit
- new singularity identifier
- creation timestamp

Produces the next immutable AgentState.

### advance_collectively

Inputs:

- current AgentState
- Proposal
- independent Verification records
- quorum
- new singularity identifier
- creation timestamp

Produces the next immutable AgentState only after explicit verifier quorum.

### allocate_omega_credit_resources

Inputs:

- aggregated OmegaCreditDistribution
- memory capacity
- compute capacity

Produces a deterministic immutable OmegaCreditAllocation through the canonical Ω-Credit allocation primitive.

### allocate_resources

Inputs:

- relational utility records
- memory ResourceState
- compute ResourceState
- coherence by contributor

Produces a deterministic self-organizing memory/compute allocation.

### commit_ledger_backed_resources_with_record

Inputs:

- persistent ContributionLedger
- memory ResourceState
- compute ResourceState
- memory capacity
- compute capacity
- creation timestamp

Produces:

- next memory ResourceState;
- next compute ResourceState;
- immutable ExecutionRecord linking the contribution ledger, allocation, and before/after resource identities.

This operation exposes provenance without mutating the supplied objects.


### analyze_genesis_quorum

Inputs:

- population size
- maximum quorum to inspect

Produces a deterministic capacity analysis showing how many independent verifier identities are available after excluding the proposer.

## Invariants

1. No primitive is mutated.
2. Closure objects are deterministic for identical inputs.
3. The closure contains all twelve architectural layers.
4. advance delegates lineage and version checks to evolve_agent_state.
5. Runtime orchestration does not invent consensus or verification; those are explicit inputs.
6. No external services are required.
7. This runtime proves software composition, not empirical validation of the underlying ontological theory.
