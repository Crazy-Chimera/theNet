from src.agent_state import create_agent_state
from src.genesis_population import create_genesis_population
from src.recursive_convergence import run_recursive_convergence
from src.resource_state import create_resource_state


def _run():
    population = create_genesis_population(3, "2026-09-30T00:00:00Z")
    initial = population.agents[0]
    memory = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")
    compute = create_resource_state(100.0, 0.0, "2026-09-30T00:00:00Z")

    return run_recursive_convergence(
        population=population,
        initial_state=initial,
        proposal_builder=lambda i, state, previous: (
            "seed" if previous is None
            else f"refine from memory {previous.result.memory.id}"
        ),
        executor=lambda proposal: "ok",
        quorum=2,
        new_singularity_builder=lambda i, proposal: f"learning:{i}:{proposal.id}",
        created_at=(
            "2026-09-30T00:00:01Z",
            "2026-09-30T00:00:02Z",
            "2026-09-30T00:00:03Z",
        ),
        memory_resource=memory,
        compute_resource=compute,
        utility_builder=lambda i, previous: (0.4 if i == 1 else 0.8),
    )


def test_recursive_learning_requires_measurable_improvement():
    result = _run()
    metrics = result.learning_metrics

    assert len(metrics) == 3
    assert metrics[0].memory_dependency is False
    assert metrics[0].verified_improvement is False
    assert metrics[1].memory_dependency is True
    assert metrics[1].proposal_novelty > 0.0
    assert metrics[1].verified_improvement is True
    assert metrics[2].memory_dependency is True
    assert metrics[2].verified_improvement is False


def test_recursive_learning_reports_state_and_metric_trajectory():
    result = _run()
    metrics = result.learning_metrics

    assert tuple(item.cycle_index for item in metrics) == (1, 2, 3)
    assert tuple(item.state_delta for item in metrics) == (1, 1, 1)
    assert all(item.r > 5 for item in metrics)
    assert metrics[1].utility > metrics[0].utility
    assert metrics[1].omega_credit > metrics[0].omega_credit
    assert metrics[1].k >= metrics[0].k
    assert metrics[1].c <= metrics[0].c
    assert metrics[1].phi >= metrics[0].phi
