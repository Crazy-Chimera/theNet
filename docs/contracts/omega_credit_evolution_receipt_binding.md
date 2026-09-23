# Iteration 35 — Ω-Credit Evolution Receipt Binding

## Purpose

Bind a verified Ω-Credit receipt to an already accepted EvolutionCommit without changing either object.

This creates a deterministic cross-layer reference between evolutionary lineage and resource-accounting evidence. It does not turn the receipt into consensus and does not claim that resource verification proves semantic correctness.

## Input

- commit: immutable EvolutionCommit.
- receipt: immutable OmegaCreditVerifiedReceipt.
- created_at: non-empty timestamp.

## Output

An immutable OmegaCreditEvolutionReceiptBinding containing:
- id
- commit_id
- receipt_id
- result_id
- created_at
- version = 1

## Acceptance rules

A binding is accepted only when:
1. commit is an EvolutionCommit.
2. receipt is an OmegaCreditVerifiedReceipt.
3. receipt.audit_valid is true.
4. all identifiers are non-empty strings.
5. created_at is non-empty.

## Identity

id is SHA-256 over the canonical commit ID, receipt ID, receipt result ID, timestamp, and version.

## Invariants

1. Same valid inputs produce the same binding ID.
2. Changing commit, receipt, result reference, or timestamp changes the binding ID.
3. The binding is immutable.
4. Neither source object is mutated.
5. Binding does not create, destroy, redistribute, or alter Ω-Credit.
6. Binding does not alter EvolutionCommit semantics.
7. A failed receipt cannot be bound.
8. Binding does not establish majority consensus or semantic truth.
9. No external service is required.

## Boundary

- EvolutionCommit records accepted proposal lineage.
- OmegaCreditVerifiedReceipt records local resource-conservation verification.
- Binding records that the two immutable artifacts were intentionally associated at a specific point.
- Later memory, expression, or system-state layers may consume the binding.

The binding is evidence linkage, not an additional truth oracle.
