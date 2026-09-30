# F10 extension — Multi-cycle recursive convergence

F10 now has two levels:

1. single-cycle convergence: proposal → verification → consensus → execution → outcome → memory → state
2. multi-cycle convergence: the resulting memory/outcome/state become inputs to the next proposal.

## Recursive invariant

Every cycle must satisfy:

- proposal.base_state_id == previous cycle state.id
- proposer remains bound to the current Agent Ω state
- verifier quorum is independent of the proposer
- the previous commit cannot be replayed
- the next state increments version exactly once
- each cycle produces a distinct outcome and memory artifact
- F10 metrics are calculated independently after the cycle completes

## Memory is now an active dependency

The proposal builder receives:

`(cycle_index, current_state, previous_cycle)`

The previous cycle exposes immutable outcome and memory identifiers. Therefore a multi-cycle test can prove that the next proposal was constructed from the preceding result rather than merely storing the result after an unrelated proposal.

## Convergence trajectory

The runtime exposes:

`state_versions`
`memory_chain`
`outcome_chain`
`all_converged`

This permits later analysis of K/C/R/Φ across N cycles instead of treating one successful cycle as global convergence.

## Current boundary

This MVP does not autonomously generate arbitrary goals, modify its own executable code, or claim AGI. The proposal builder and executor remain explicit dependency-injection boundaries.