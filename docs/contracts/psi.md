# Ψ Expression — Contract

## Purpose

Ψ is the expression layer. It records a deterministic association between an established Π meaning and an explicit expression reference. Expression is the boundary where internal meaning becomes externally addressable, without executing or asserting the correctness of the expression.

## Input

- meaning_id: non-empty string identifying a Π result.
- expression_id: non-empty string identifying the explicit expression reference.
- created_at: non-empty timestamp string.

## Output

An immutable Expression containing:
- id
- meaning_id
- expression_id
- created_at
- version = 1

## Identity

id is SHA-256 over canonical JSON of the three inputs and version.

## Invariants

1. Reject empty or non-string inputs.
2. Same inputs produce the same identity.
3. Changing meaning or expression changes identity.
4. Input values are not mutated.
5. Ψ records an expression association; it does not execute the expression.
6. Ψ does not establish truth, safety, consensus, contribution value, or convergence.
7. Expression remains explicitly attributable to its Π meaning.
8. No external services.

## Boundary

Π associates a converged state with a contribution reference. Ψ associates that meaning with an expression reference. Execution, self-modeling, safety, and system-level redefinition remain separate concerns.
