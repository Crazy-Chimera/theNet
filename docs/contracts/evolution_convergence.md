# Verified Evolution Γ Convergence Contract

## Purpose

Bind the verified ΦΩ² resonance of an Agent Ω evolution context to an explicit Γ convergence decision.

## Input

- `Resonance` produced from the verified evolution structure and Ω² memory.
- one or more candidate state IDs.
- one selected candidate state ID.
- non-empty `created_at`.

## Process

VERIFIED ΦΩ² RESONANCE + CANDIDATE STATES → Γ CONVERGENCE

## Output

An immutable `EvolutionConvergence` containing:
- the exact input resonance;
- the deterministic `Convergence` decision;
- `created_at`.

## Invariants

1. The resonance must already be an immutable `Resonance`.
2. Candidate states must satisfy the canonical Γ convergence contract.
3. The selected state must be one of the candidates.
4. The exact resonance ID is preserved; no new structural identity is inferred.
5. Equal inputs produce equal output identity through the contained convergence record.
6. Source objects are never mutated.
7. Γ selects a candidate; it does not claim that selection is network-wide consensus.
8. The integration does not independently establish truth, meaning, or safety.
9. No external services are required.
