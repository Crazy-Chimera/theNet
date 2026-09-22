# Verified Evolution Memory Contract

## Purpose

Connect a successful Agent Ω collective evolution to Ω² persistent memory.

The memory layer records the verified evolution commit as provenance. It does not independently establish truth or consensus.

## Input

- immutable CollectiveEvolution
- non-empty subject_id
- non-empty created_at

## Process

COLLECTIVE EVOLUTION → VERIFIED COMMIT → Ω² MEMORY

The memory source is the resulting EvolutionCommit.id.

## Output

An immutable EvolutionMemory containing:

- evolution
- memory

The memory record uses:

- subject_id as the evolved agent;
- source_id = evolution.commit.id;
- kind = "verified-evolution".

## Invariants

1. The evolution must already have reached consensus and produced a commit.
2. The memory source must be exactly the verified commit ID.
3. Memory creation does not mutate the evolution or its state.
4. Equal inputs produce equal memory identity.
5. No external service is required.
6. Ω² records provenance; it does not re-verify the evolution.

## Boundary

Collective evolution decides whether a state transition is authorized. Ω² preserves a reference to that verified transition so later resonance, learning, and self-modeling can consume it.
