# Π Meaning — Contract

## Purpose
Π is the meaning/contribution layer. It records a deterministic association between a converged state and a declared contribution reference. It does not generate semantic truth, execute an action, or override Γ.

## Input
- convergence_id: non-empty string identifying a Γ result.
- contribution_id: non-empty string identifying the declared contribution reference.
- created_at: non-empty timestamp string.

## Output
An immutable Meaning: id, convergence_id, contribution_id, created_at, version = 1.

## Identity
id is SHA-256 over canonical JSON of the three inputs and version.

## Invariants
1. Reject empty or non-string inputs.
2. Same inputs produce the same identity.
3. Changing convergence or contribution changes identity.
4. The input values are not mutated.
5. Π records an association; it does not claim that the contribution is true, useful, safe, or accepted.
6. Π does not execute expression or modify memory.
7. No external services.

## Boundary
Γ establishes exact agreement. Π associates that agreed state with a contribution reference. Ψ later handles expression/action. Θ, Σ, and higher verification layers remain separate.