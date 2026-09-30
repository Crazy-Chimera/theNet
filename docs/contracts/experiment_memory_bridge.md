# V1.9 — Ledger → Ω² Memory Bridge

A fingerprint identifies an experiment design and observed deterministic result; it does not by itself constitute verification.

Memory admission requires two distinct immutable ledger records whose fingerprints agree on design, result, baseline graph, and runtime contract.

When that comparison succeeds, the bridge creates an immutable MemoryRecord with source_id equal to the baseline ledger id and kind equal to verified-experiment.

A changed hypothesis, mismatched reproduction, self-verification, or tampered ledger identity remains outside Ω² Memory.

The bridge is descriptive and deterministic. It does not modify consensus, replay, counterfactual execution, credit, or experiment results.
