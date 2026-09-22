# Ω-Credit Self-Organizing Runtime Contract

## Purpose

Expose the end-to-end local self-organizing resource transition through the Agent Ω runtime facade.

The runtime composes existing pure layers:

verified relational utility + Φ coherence -> Ω-Credit allocation -> Resource State transition

The facade performs no external resource transfer and does not create verification, consensus, reputation, or meaning.

## Input

- a finite collection of RelationalUtility records
- immutable memory ResourceState
- immutable compute ResourceState
- contributor -> Φ coherence mapping
- non-empty creation timestamp

## Output

An immutable pair:

- next memory ResourceState
- next compute ResourceState

## Invariants

1. Verification and Φ coherence are delegated to canonical primitives.
2. Unverified utility receives no allocation.
3. Missing contributor coherence is rejected.
4. Resource capacity is not exceeded.
5. Input resource states are not mutated.
6. Repeated identical inputs produce identical output states.
7. The runtime facade does not duplicate allocation logic.
8. No external service is required.
