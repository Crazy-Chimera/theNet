# Iteration 43 — Evolution History Root Anchor Contract

## Purpose

Anchor a verified evolution-history root to the immediately preceding history root.

The anchor creates a deterministic transition between two already identified history roots without changing either root.

## Input

- `previous_root_id`: optional root identifier for the preceding epoch.
- `current_root_id`: non-empty current root identifier.
- `created_at`: non-empty timestamp.
- `version`: protocol version, initially `1`.

The first epoch may omit `previous_root_id`.

## Output

Immutable `EvolutionHistoryRootAnchor`:

- `id`
- `previous_root_id`
- `current_root_id`
- `created_at`
- `version`

## Invariants

1. `current_root_id` must be non-empty.
2. If supplied, `previous_root_id` must be non-empty.
3. `created_at` must be non-empty.
4. The anchor is immutable.
5. The same normalized input produces the same anchor identity.
6. Changing either root changes the anchor identity.
7. Changing the timestamp changes the anchor identity.
8. The first epoch can be anchored without a previous root.
9. The anchor does not modify either root.
10. The anchor does not itself prove that either root is valid; root verification remains a separate gate.
11. No external services are required.

## Boundary

Iteration 42 verifies a history root against its supplied local history.

Iteration 43 links successive verified roots into an explicit evolution-history chain.

Later layers may use this chain for continuity checks, synchronization, persistence, and collective evolution evidence.
