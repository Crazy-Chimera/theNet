# Iteration 40 — Evolution History Integrity Contract

## Purpose

Replay protection prevents the same evolution from being applied twice. It does
not by itself prove that a supplied history forms a coherent causal chain.

Iteration 40 adds a read-only history audit. The audit verifies that each
EvolutionCommit is structurally linked to the state it claims to follow and
that the history contains no replayed application.

The audit does not choose between competing valid branches. A branch is a
structural fact that remains available for later convergence or policy.

## Input

- `commits`: finite iterable of `EvolutionCommit` records.
- `initial_state_id`: optional non-empty state identifier.
- `current_state_id`: optional non-empty state identifier.

## Output

An immutable `EvolutionHistoryAudit` containing:

- `valid`: whether all supplied records pass the integrity checks.
- `commit_ids`: canonical ordered tuple of commit IDs.
- `head_state_ids`: sorted tuple of states produced as commit successors.
- `branch_state_ids`: sorted tuple of predecessor states with more than one
  distinct successor commit.
- `error_count`: number of integrity violations.

## Integrity rules

1. Every record must be an `EvolutionCommit`.
2. Commit IDs must be unique.
3. A commit's `previous_state_id` must be non-empty.
4. When `initial_state_id` is supplied, the first commit must target it.
5. For each adjacent record in the supplied canonical sequence, the next
   commit must target the state produced by the previous commit when a
   successor state is explicitly available.
6. Replay of the same proposal on the same previous state is invalid.
7. Multiple distinct successors from one predecessor are reported as a branch,
   not automatically rejected.
8. The audit is deterministic and does not mutate input.
9. No external services are required.
10. The audit does not perform consensus, convergence, meaning, or policy
    selection.

## Scope

This is an integrity/audit primitive. It does not calculate the resulting
AgentState IDs because those require the full state-transition context
(including the new singularity and creation timestamp).

Therefore the audit validates the portion of causal history represented by
EvolutionCommit records and explicitly reports what it cannot establish.

## Required Tests

Tests cover:

- empty history;
- valid unique history;
- duplicate commit detection;
- replay detection;
- invalid record type;
- invalid initial-state anchor;
- branch detection without rejection;
- immutable audit output;
- deterministic result;
- input non-mutation.
