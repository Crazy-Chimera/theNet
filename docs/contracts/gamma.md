# Γ Convergence — Contract

## Purpose
Γ is the convergence layer. It determines whether a set of proposed state identifiers has reached exact structural agreement. It normalizes proposal order but does not invent a winner or infer majority consensus.

## Input
- proposals: iterable of non-empty string state identifiers.
- Empty proposal collections are invalid because no convergence claim can be made.

## Output
An immutable Convergence:
- id: SHA-256 fingerprint of canonical convergence input
- proposal_ids: sorted proposal identifiers
- resolved_id: the common identifier when all proposals agree, otherwise null
- converged: true only when all proposals are identical
- version = 1

## Invariants
1. Reject an empty proposal collection.
2. Reject non-string or empty proposal identifiers.
3. Preserve multiplicity; repeated observations are not silently discarded.
4. Proposal ordering does not affect identity.
5. converged is true exactly when all proposal identifiers are equal.
6. resolved_id is set only for exact agreement.
7. Γ does not choose a winner among conflicting proposals.
8. Γ does not establish quorum, trust, consensus, meaning, contribution, or safety.
9. No external services.

## Boundary
Ω produces state transitions. Ω² persists observations. Φ represents structure. Γ evaluates exact agreement among proposed identifiers. Higher layers may apply verification, quorum, reputation, or governance rules.