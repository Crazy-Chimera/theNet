# Execution Audit Contract — Iteration 25

## Purpose

Expose the immutable execution ledger through a queryable audit surface. The surface allows an execution chain to be retrieved by execution-record identity or contribution-ledger identity without exposing mutable internal state.

## Input

- ExecutionRecord objects.
- Query identity: execution record ID or contribution ledger ID.

## Output

An immutable ExecutionAudit containing:
- execution_ledger
- records

Query operations:
- find_record(record_id) → ExecutionRecord or None
- find_records_by_contribution_ledger(ledger_id) → tuple[ExecutionRecord, ...]
- ledger_id → immutable ExecutionLedger identity

## Invariants

1. Audit input contains only ExecutionRecord objects.
2. Duplicate record identities are rejected.
3. The execution ledger is derived deterministically from the supplied records.
4. Records are stored canonically by record ID.
5. Queries return immutable record objects and tuples.
6. Unknown record IDs return None.
7. Unknown contribution-ledger IDs return an empty tuple.
8. Querying never mutates the audit or its records.
9. The audit does not create or infer verification, consensus, or causal truth.
10. No external service is required.

## Runtime boundary

The runtime facade may expose audit construction and query helpers. It remains orchestration only; the audit surface is a read-only projection over explicit immutable execution records.