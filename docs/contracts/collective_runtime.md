# Collective Computation Runtime v2.7 Contract

## Purpose

Close one complete Agent Ω collective-computation cycle without introducing a new consensus algorithm or mutating existing domain objects.

The runtime composes:

PROPOSAL → VERIFICATION → CONSENSUS → Γ CONVERGENCE → SANDBOX EXECUTION → OUTCOME → RELATIONAL UTILITY → Φ COHERENCE → Ω-CREDIT → RESOURCE ALLOCATION → EXECUTION PROVENANCE → MEMORY → STATE

## Input

- current immutable AgentState;
- Proposal targeting that state;
- independent valid Verification records;
- explicit quorum;
- new singularity identifier;
- creation timestamp;
- memory and compute ResourceState;
- injected executor callable;
- optional utility value in [0, 1];
- optional prior evolution commits for replay protection.

## Executor boundary

The executor receives only the immutable proposal and must return a string result.

The MVP does not claim that the callable is a secure process sandbox. A production sandbox remains an infrastructure boundary. The runtime only treats the executor as the execution boundary and records its measured result immutably.

## Output

CollectiveComputationResult contains:

- Consensus;
- Γ Convergence;
- EvolutionCommit;
- ExecutionRecord;
- ComputationOutcome;
- Ω² MemoryRecord;
- verifier Relation records;
- Φ structure;
- verified RelationalUtility;
- Ω-Credit;
- contribution ledger;
- next memory and compute resource states;
- next immutable AgentState.

## Ordering invariant

Canonical agent state is not advanced until:

1. consensus has reached quorum;
2. the executor has returned a result;
3. the outcome has been materialized;
4. verified relational utility and Ω-Credit have been constructed;
5. resource allocation and execution provenance have been constructed;
6. replay protection has passed.

If execution fails, the supplied state and resource objects remain unchanged because all domain objects are immutable.

## Credit rule

The runtime uses the existing Ω-Credit primitive:

credit = verified relational utility × resource efficiency × Φ coherence

Unverified utility cannot produce positive Ω-Credit.

## Consensus boundary

Consensus remains distinct from Γ convergence:

- Consensus answers whether the declared quorum of independent valid verifiers was reached.
- Γ convergence records the resolved proposal identity.
- Neither primitive claims that consensus itself establishes empirical truth.

## Recursion

The resulting state and memory form the input surface for a subsequent proposal:

Cₙ → outcomeₙ → memoryₙ → stateₙ → proposalₙ₊₁ → Cₙ₊₁

This is the MVP collective-computation feedback loop.

## Non-goals

v2.7 does not implement:

- autonomous code mutation;
- a new global consensus protocol;
- Sybil resistance;
- empirical truth inference from majority alone;
- a production-grade secure sandbox;
- a claim that the theoretical Φ/Ω model is established physics.
