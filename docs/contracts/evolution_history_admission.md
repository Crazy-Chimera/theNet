# Iteration 46 — Evolution History Admission Gate Contract

## Purpose

The history-verification layer establishes that a supplied evolution chain is internally consistent. Iteration 46 turns that verification result into an explicit admission boundary for the next evolutionary commit.

The gate answers only:

> Is this candidate evolution admissible under the supplied local history verification?

It does not decide whether an evolution is globally true, optimal, or accepted by a distributed consensus.

## Input

- candidate_commit: an existing EvolutionCommit.
- history_audit: an EvolutionHistoryAudit.
- current_state_id: the state from which the candidate claims to evolve.
- expected_convergence_id: the convergence context required by the candidate.

## Output

Immutable EvolutionAdmission:

- admissible
- candidate_id
- current_state_id
- convergence_id
- reason
- version = 1

## Invariants

1. Candidate must be an EvolutionCommit.
2. History audit must be valid.
3. Current state must be non-empty.
4. Candidate.previous_state_id must equal current_state_id.
5. Candidate.convergence_id must equal expected_convergence_id.
6. Invalid history always rejects admission.
7. State mismatch rejects admission.
8. Convergence mismatch rejects admission.
9. The candidate is not mutated.
10. Verification remains local; this is not a consensus proof.
11. The gate does not rank or optimize candidates.
12. No external services are required.

## Boundary

EvolutionHistory verification establishes integrity.

EvolutionHistoryAdmission decides whether a candidate may cross into the next local evolution step.

The intended path is:

EvolutionCommit
→ History Audit
→ History Verification
→ Admission Gate
→ next verified evolution

This is the minimum control boundary required before autonomous recursive evolution can safely consume its own history.
