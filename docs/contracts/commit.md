# Verified Evolution Commit Contract

## Purpose

A commit is the first state transition that turns a proposal into a new Agent Ω state. It is allowed only when the proposal targets the current state, the supplied verifications are valid, and Γ reports exact convergence on that proposal.

This primitive deliberately does not implement majority quorum, reputation weighting, resource allocation, or governance. Exact convergence is a stronger and narrower condition than majority consensus.

## Input

- current_state_id: non-empty Agent Ω state identifier.
- proposal_id: non-empty proposal identifier.
- proposal_base_state_id: non-empty base state identifier.
- verification_ids: finite iterable of non-empty verification identifiers.
- all_verifications_valid: boolean indicating that every supplied verification passed the external verification policy.
- convergence_id: non-empty Γ convergence identifier.
- converged: boolean result from Γ.
- resolved_id: resolved proposal identifier from Γ, or null.
- created_at: non-empty timestamp.

## Output

An immutable EvolutionCommit:

- id
- previous_state_id
- proposal_id
- verification_ids
- convergence_id
- created_at
- version = 1

## Commit rule

A commit is accepted only if:

1. current_state_id equals proposal_base_state_id;
2. verification_ids is non-empty;
3. all_verifications_valid is true;
4. converged is true;
5. resolved_id equals proposal_id.

Otherwise the constructor rejects the commit.

## Identity

The commit ID is SHA-256 over canonical previous state, proposal, sorted unique verification IDs, convergence ID, timestamp, and version.

## Invariants

1. No state is mutated.
2. Same valid inputs produce the same commit ID.
3. Verification identifiers are normalized deterministically.
4. A rejected commit produces no commit object.
5. A proposal based on another state cannot commit onto the current state.
6. A non-converged Γ result cannot commit.
7. A convergence result resolving to another proposal cannot commit.
8. Invalid verification policy cannot commit.
9. The commit records lineage; it does not itself implement memory or learning.
10. No external service is required.

## Boundary

Proposal expresses intent.

Verification supplies evidence claims.

Γ evaluates exact agreement.

Commit creates a new immutable evolutionary event that later state-transition and memory layers can consume.

## Important limitation

This contract does not claim that exact convergence is sufficient for real-world truth or safety. It only defines the deterministic software gate used by this layer.