# F10.3 — Resource–Learning Feedback Loop

F10.3 turns F10.2 from a future allocation plan into a causal input to the next
recursive computation cycle.

## Contract

For a recursive run:

1. A cycle produces an immutable collective outcome.
2. F10.1 measures recursive learning from the cycle history.
3. F10.2 converts the measured history into weighted resource shares.
4. The share assigned to the most recent cycle becomes the memory/compute
   budget presented to the next cycle.
5. The next proposal therefore executes under resources determined by verified
   prior experience.

The feedback capacity is finite and explicitly supplied. F10.3 does not create
resources.

## Cumulative allocation

The allocator receives the complete learning history available at the feedback
point, not only the latest metric.

For cycle i:

weight_i = Ω-Credit_i × (1 + bonus) when verified_improvement_i = true,
otherwise Ω-Credit_i.

The next cycle receives the latest cycle's normalized share of the finite
feedback budget.

Therefore an improvement changes the next cycle's resource share relative to
the preceding history. A single metric alone would always receive 100% and
would not constitute meaningful adaptive allocation.

## Resource-state transition

The allocated share is materialized as a new immutable ResourceState with
zero initial usage. That state is passed directly into the next
run_collective_computation invocation.

The execution provenance therefore records the feedback boundary through
memory_before_id and compute_before_id.

## Safety invariants

- Only measured F10.1 metrics can affect the feedback allocation.
- Unverified improvement receives no adaptive bonus.
- The bonus remains bounded to [0, 1].
- The feedback budget is finite and externally supplied.
- Allocation cannot exceed that budget.
- Resource states remain immutable.
- The next cycle cannot influence the resources that were already used to
  produce its own evidence.
- No agent code, goals, or verifier rules are changed by F10.3.
- Determinism is preserved for identical inputs.

## Architectural closure

EXPERIENCE → VERIFICATION → CONSENSUS → OUTCOME → RELATIONAL UTILITY
→ Ω-CREDIT → F10 CONVERGENCE → F10.1 VERIFIED IMPROVEMENT
→ F10.2 ADAPTIVE ALLOCATION → F10.3 RESOURCE FEEDBACK
→ NEXT CYCLE → NEW EXPERIENCE

F10.3 therefore closes the operational resource-learning loop without making
the stronger claim that the loop constitutes general intelligence or
consciousness.
