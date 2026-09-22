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

## Invariants

1. No primitive is mutated.
2. Closure objects are deterministic for identical inputs.
3. The closure contains all twelve architectural layers.
4. advance delegates lineage and version checks to evolve_agent_state.
5. Runtime orchestration does not invent consensus or verification; those are explicit inputs.
6. No external services are required.
7. This runtime proves software composition, not empirical validation of the underlying ontological theory.
