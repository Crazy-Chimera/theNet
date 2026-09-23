# Iteration 36 — Collective Evolution Evidence

## Purpose

Aggregate verified Ω-Credit evolution-receipt bindings into one immutable evidence object for a collective evolution step.

The object records which already-verified execution artifacts are associated with the step. It does not create credits, verify semantics, or establish majority consensus.

## Input

- \`bindings\`: iterable of \`OmegaCreditEvolutionReceiptBinding\`.
- \`created_at\`: non-empty timestamp.

## Output

Immutable \`CollectiveEvolutionEvidence\`:

- \`id\`
- \`binding_ids\`
- \`commit_ids\`
- \`receipt_ids\`
- \`result_ids\`
- \`created_at\`
- \`version = 1\`

## Invariants

1. Every input item must be an \`OmegaCreditEvolutionReceiptBinding\`.
2. Every binding must contain non-empty identifiers.
3. Input order does not affect identity.
4. Duplicate binding IDs are represented once.
5. The corresponding commit, receipt, and result references are preserved.
6. Empty binding collections are valid.
7. Output is immutable.
8. Source bindings are not mutated.
9. The same valid inputs produce the same evidence ID.
10. Changing a binding set or timestamp changes the evidence ID.
11. Evidence does not mint, burn, redistribute, or alter Ω-Credit.
12. Evidence does not establish semantic truth, majority consensus, or external validity.
13. No external service is required.

## Boundary

- EvolutionCommit records accepted proposal lineage.
- Ω-Credit verified receipt records local resource-conservation verification.
- Evolution receipt binding associates those artifacts.
- Collective evolution evidence groups such bindings into a deterministic evidence surface.
- Later consensus, memory, convergence, or learning layers may consume this evidence.

The evidence object is aggregation, not an additional truth oracle.
