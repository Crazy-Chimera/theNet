# Iteration 5 — Φ Structure Verification

## Scope

Verify the canonical Φ structural primitive after the final contract alignment.

## Verified locally by specification

- Φ accepts only Relation objects.
- Empty relation collections produce an immutable empty structure.
- Relation IDs are deduplicated.
- Node IDs are derived from relation endpoints.
- Directed edges preserve source → target.
- Input ordering does not affect the canonical identity.
- Structural changes affect the identity.
- Φ does not infer meaning, verify relations, or perform consensus.

## CI gate

This document is committed with the current Φ contract state so GitHub Actions executes the complete package-build, runtime-smoke, and pytest suite against the same revision.

Completion requires a successful CI run on this commit.