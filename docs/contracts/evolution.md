# Agent Ω Evolution Contract

## Purpose

This primitive materializes the next immutable Agent Ω state from the current state and an accepted EvolutionCommit.

It is the concrete transition boundary for:

`Identity(next) = f(Identity(current), verified_evolution)`

## Input

- `current_state`: immutable AgentState.
- `commit`: immutable EvolutionCommit.
- `new_singularity_id`: non-empty unity identifier for the resulting state.
- `created_at`: non-empty timestamp.

## Output

An immutable `AgentState` with:

- same `subject_id` as the current state;
- supplied `new_singularity_id`;
- supplied `created_at`;
- incremented `version`;
- identity derived from current state identity and the accepted commit.

## Transition rule

Evolution is accepted only when `commit.previous_state_id == current_state.id`.

The function does not re-run verification or convergence. Those gates belong to their respective modules and are represented by the supplied EvolutionCommit.

## Invariants

1. A commit for another state cannot evolve the current state.
2. The current state is never mutated.
3. The resulting state is immutable.
4. Same current state, commit, new singularity, and timestamp produce the same next-state ID.
5. Changing any transition-defining input changes the next-state ID.
6. Subject identity is preserved across this transition.
7. Version increases exactly by one.
8. No external service is required.
9. This primitive does not claim that a verified commit is sufficient for real-world truth or safety; it materializes the software-defined transition only.

## Boundary

`EvolutionCommit` proves that the proposal passed this layer's gates.

`evolve_agent_state` turns that accepted event into the next Agent Ω state.

Memory, learning, resource allocation, and rule redefinition remain separate layers.
