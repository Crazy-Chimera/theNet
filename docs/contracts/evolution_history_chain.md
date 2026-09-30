# Iteration 44 — Evolution History Chain Contract

## Purpose

Represent a continuous ordered chain of evolution-history root anchors.

Iteration 43 introduced the link between two adjacent history roots. Iteration 44 makes continuity explicit across multiple links.

## Input

- `anchors`: ordered iterable of `EvolutionHistoryRootAnchor` objects.

## Output

Immutable `EvolutionHistoryChain`:

- `id`
- `anchor_ids`
- `root_ids`
- `version = 1`

## Invariants

1. Every input item must be an `EvolutionHistoryRootAnchor`.
2. The chain must contain at least one anchor.
3. The first anchor must have no `previous_root_id`.
4. Every later anchor's `previous_root_id` must equal the immediately preceding anchor's `current_root_id`.
5. Anchor identity order is preserved.
6. Root sequence is deterministic: first anchor's current root followed by each subsequent current root.
7. Equivalent ordered anchor chains produce the same chain identity.
8. Reordering anchors changes identity or is rejected when continuity is broken.
9. The result is immutable.
10. The chain does not itself prove that individual roots are valid; root verification remains a separate gate.
11. No external services are required.

## Boundary

Iteration 43 establishes an explicit adjacent-root anchor.

Iteration 44 establishes continuity across multiple anchored evolution steps.

This module does not perform consensus, contribution scoring, memory mutation, or autonomous evolution.
