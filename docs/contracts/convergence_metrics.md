# F10 — Convergence Metrics Engine

TheNet F10 measures operational convergence from immutable runtime artifacts.

These metrics are project-level engineering metrics. They are not measurements of physical reality and do not establish that the Φ/Ω theoretical framework is physically true.

## Metrics

### K — invariant consistency

K = passed invariant checks / total invariant checks.
The runtime checks consensus, Γ convergence, proposal resolution, outcome success, verified utility, memory linkage, evidence linkage, commit state linkage, and exactly-one-version state advancement.
Acceptance threshold: K > 0.8.

### C — structural complexity proxy

C measures excess branching/redundancy relative to a minimal connected single-candidate structure.
- excess candidates = max(candidate_count - 1, 0)
- excess edges = max(edge_count - (node_count - 1), 0)
- denominator = candidate_count + (node_count - 1) + max(edge_count, 1)
C is bounded to [0, 1]. Acceptance threshold: C < 0.3.
This is intentionally a structural proxy, not a universal theory of complexity.

### R — verified recursive depth

R is the number of links in the explicit artifact chain:
state → proposal → consensus → convergence → outcome → utility → memory → commit → next state.
The chain must contain unique artifact identifiers. Acceptance threshold: R > 5.
R measures a verified causal artifact chain, not intelligence, self-awareness, or unrestricted recursive self-improvement.

### Φ — relational coherence

Φ is derived from the existing phi_coherence() primitive: the fraction of nodes contained in the largest weakly connected component of the Φ structure.
Acceptance threshold: Φ > 0.7.

## F10 convergence condition

A cycle is operationally converged only when K > 0.8, C < 0.3, R > 5, and Φ > 0.7.

Metrics are computed after runtime artifacts are constructed. They do not participate in consensus, execution, credit creation, resource allocation, or state mutation. This avoids the metrics engine grading its own inputs.

## Current MVP interpretation

For the v2.7 single-proposal collective runtime, the canonical happy path is a minimal connected verifier structure with one converged candidate and a nine-artifact chain. Under these definitions it enters the target operational region when the independent runtime invariants pass.

## Non-goals

F10 does not claim empirical truth from consensus alone, that majority agreement implies correctness, that Φ is a physical observable, that R measures AGI capability, that C is a universal complexity measure, or that one successful cycle proves global convergence.