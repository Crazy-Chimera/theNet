# Iteration 11 — Ψ Expression Verification

Status: PENDING CI

## Scope

Ψ is the expression layer. It binds a Π meaning record to an explicit expression reference without executing the expression or asserting its correctness.

## Verified implementation

- Contract: `docs/contracts/psi.md`
- Implementation: `src/expression.py`
- Tests: `tests/test_expression.py`
- Integration test: `tests/test_expression_integration.py`

## Contract properties

- required identifiers and timestamp are validated
- identity is deterministic
- changing meaning or expression changes identity
- output is immutable
- Π meaning remains explicitly attributable through `meaning_id`
- Ψ does not execute the expression
- Ψ does not establish truth, safety, consensus, contribution value, or convergence
- no external service dependency

## Integration

The added integration test verifies the concrete boundary:

`Π meaning -> Ψ expression`

The expression references the exact immutable meaning identity rather than copying or redefining it.

## Verification gate

GitHub Actions must pass package build, package installation, runtime smoke test, and the complete pytest suite against the final verification revision.

## Result

Pending CI execution.

## Boundary

Π associates a converged state with a contribution reference. Ψ associates that meaning with an expression reference. Execution and later self-model/safety layers remain separate.
