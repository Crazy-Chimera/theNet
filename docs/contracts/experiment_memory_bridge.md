# V1.9 — Ledger → Ω-Memory Bridge

A fingerprint identifies a reproducible experiment; it does not itself constitute verification.

The bridge creates an immutable Ω² MemoryRecord only when an explicit non-empty verification reference is supplied and the ledger identity still matches its result fingerprint.

Memory uses:
- source_id = ledger.id
- kind = verified-experiment
- subject_id and created_at supplied by the caller

The bridge does not modify consensus, replay, counterfactual execution, credit, or experiment results.
