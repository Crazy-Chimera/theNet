# Iteration 12 — Θ Self-Knowledge Verification

Status: PENDING CI

## Scope

Θ is the self-model layer. It records a deterministic self-reference connecting a subject to a Φ structural state and an Ω² memory state.

## Reviewed implementation

- Contract: `docs/contracts/theta.md`
- Implementation: `src/self_knowledge.py`
- Tests: `tests/test_self_knowledge.py`

## Contract properties

- required identifiers and timestamp are validated
- identity is deterministic
- changing any defining input changes identity
- output is immutable
- inputs are not mutated
- Θ references state without mutating it
- Θ does not claim consciousness, intelligence, truth, autonomy, verification, consensus, meaning, or contribution
- no external service dependency

## Verification gate

GitHub Actions must pass package build, package installation, runtime smoke test, and the complete pytest suite against this revision.

## Result

Pending CI execution.

## Boundary

Φ provides structural state. Ω² provides persistent memory. Θ binds a subject to both as an explicit self-reference. Ρ can later connect multiple self-models through relational co-definition.
