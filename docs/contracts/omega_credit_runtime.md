# Ω-Credit Runtime Allocation Facade Contract

## Purpose

Expose the deterministic Ω-Credit distribution → resource allocation pipeline through the Agent Ω runtime facade.

The facade composes existing pure layers:

`Ω-Credit records → Ω-Credit distribution → memory/compute allocation`

It does not alter the underlying credit or resource primitives.

## Input

- `OmegaCreditDistribution`
- finite non-negative `memory_capacity`
- finite non-negative `compute_capacity`

## Output

An immutable `OmegaCreditAllocation`.

## Invariants

1. The facade delegates distribution allocation to the canonical Ω-Credit allocation primitive.
2. Invalid distribution or capacities are rejected by the canonical primitive.
3. The input distribution is not mutated.
4. Identical inputs produce identical allocation identity.
5. No external service is required.
6. The facade does not create new contribution scores.
7. The facade does not establish verification or consensus.
8. Resource mutation remains outside the facade.

## Architectural role

The facade makes the Ω-Credit resource path available to Agent Ω without duplicating allocation logic.

`verified relational utility + resource state + Φ-derived coherence → Ω-Credit → contribution distribution → resource allocation`
