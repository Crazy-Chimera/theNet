import pytest

from src.agent_state import create_agent_state
from src.genesis_population import create_genesis_population
from src.recursive_convergence import run_recursive_convergence
from src.resource_state import create_resource_state


def _build():
    population = create_genesis_population(3, "2026-09-30T00:00:00Z")
    initial = population.agents[0]
    memory = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
    compute = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
    return population, initial, memory, compute


def test_recursive_convergence_advances_through_multiple_cycles():
    population, initial, memory, compute = _build()
    seen = []

    def proposal_builder(index, state, previous):
        seen.append((index, state.version, previous.result.memory.id if previous else None))
        if previous is None:
            return "observe initial outcome"
        return f"refine from memory {previous.result.memory.id}"

    result = run_recursive_convergence(
        population=population,
        initial_state=initial,
        proposal_builder=proposal_builder,
        executor=lambda proposal: f"executed:{proposal.proposal}",
        quorum=2,
        new_singularity_builder=lambda index, proposal: f"recursive:{index}:{proposal.id}",
        created_at=(
            "2026-09-30T00:00:01Z",
            "2026-09-30T00:00:02Z",
            "2026-09-30T00:00:03Z",
        ),
        memory_resource=memory,
        compute_resource=compute,
    )

    assert result.cycle_count == 3
    assert result.state_versions == (2, 3, 4)
    assert result.final_state.version == 4
    assert result.all_converged is True
    assert seen[0] == (1, 1, None)
    assert seen[1][1] == 2
    assert seen[1][2] == result.cycles[0].result.memory.id
    assert seen[2][2] == result.cycles[1].result.memory.id
    assert len(set(result.memory_chain)) == 3
    assert len(set(result.outcome_chain)) == 3


def test_recursive_convergence_is_deterministic():
    args = _build()
    kwargs = dict(
        population=args[0],
        initial_state=args[1],
        proposal_builder=lambda i, state, previous: (
            "seed" if previous is None else f"continue:{previous.result.outcome.id}"
        ),
        executor=lambda proposal: "ok",
        quorum=2,
        new_singularity_builder=lambda i, proposal: f"s:{i}:{proposal.id}",
        created_at=("2026-09-30T00:00:01Z", "2026-09-30T00:00:02Z"),
        memory_resource=args[2],
        compute_resource=args[3],
    )
    first = run_recursive_convergence(**kwargs)

    args2 = _build()
    kwargs["population"] = args2[0]
    kwargs["initial_state"] = args2[1]
    kwargs["memory_resource"] = args2[2]
    kwargs["compute_resource"] = args2[3]
    second = run_recursive_convergence(**kwargs)

    assert first == second


def test_recursive_convergence_rejects_insufficient_quorum():
    population, initial, memory, compute = _build()

    with pytest.raises(ValueError, match="supported by independent verifiers"):
        run_recursive_convergence(
            population=population,
            initial_state=initial,
            proposal_builder=lambda i, state, previous: "proposal",
            executor=lambda proposal: "ok",
            quorum=3,
            new_singularity_builder=lambda i, proposal: "next",
            created_at=("2026-09-30T00:00:01Z",),
            memory_resource=memory,
            compute_resource=compute,
        )
