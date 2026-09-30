# Iteration 40 — Evolution History Integrity Contract

## Purpose

Replay protection prevents the same evolution from being applied twice. It does
not by itself provide a compact audit of the supplied EvolutionCommit history.

Iteration 40 adds a read-only history audit. The audit checks the integrity
that can be established from EvolutionCommit records alone.

The audit does not choose between competing valid branches. A branch is a
structural fact that remains available for later convergence or policy.

## Input

- `commits`: finite iterable of `EvolutionCommit` records.
- `initial_state_id`: optional non-empty state identifier used as an anchor.

## Output

An immutable `EvolutionHistoryAudit` containing:

- `valid`: whether all supplied records pass the audit checks.
- `commit_ids`: canonical ordered tuple of commit IDs.
- `predecessor_state_ids`: sorted tuple of referenced previous-state IDs.
- `branch_state_ids`: sorted tuple of predecessor states with more than one
  distinct proposal commit.
- `error_count`: number of integrity violations.

## Integrity rules

1. Every record must be an `EvolutionCommit`.
2. Commit IDs must be unique.
3. A commit's `previous_state_id` must be non-empty.
4. When `initial_state_id` is supplied, at least one commit must target it.
5. Replay of the same proposal on the same previous state is invalid.
6. Multiple distinct proposals from one predecessor are reported as a branch,
   not automatically rejected.
7. The audit is deterministic and does not mutate input.
8. No external services are required.
9. The audit does not perform consensus, convergence, meaning, or policy
   selection.

## Explicit limitation

An EvolutionCommit contains the state it follows, but not the successor
AgentState ID. Therefore this audit cannot prove full adjacent state-chain
continuity or compute a unique head state from commits alone.

Those claims require the corresponding AgentState transition records.

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
