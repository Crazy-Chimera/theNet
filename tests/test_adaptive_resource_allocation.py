from src.adaptive_resource_allocation import create_adaptive_resource_allocation
from src.recursive_learning_metrics import RecursiveLearningMetrics


def _metric(index, credit, improved):
    return RecursiveLearningMetrics(
        cycle_index=index,
        proposal_novelty=0.5,
        utility=0.5,
        omega_credit=credit,
        resource_efficiency=0.8,
        k=1.0,
        c=0.0,
        r=8,
        phi=1.0,
        state_delta=1,
        memory_dependency=index > 1,
        verified_improvement=improved,
    )


def test_verified_improvement_receives_bounded_adaptive_bonus():
    result = create_adaptive_resource_allocation(
        (
            _metric(1, 1.0, False),
            _metric(2, 1.0, True),
        ),
        memory_capacity=100.0,
        compute_capacity=200.0,
        improvement_bonus=0.25,
    )

    assert result.memory_by_cycle[1][1] > result.memory_by_cycle[0][1]
    assert result.compute_by_cycle[1][1] > result.compute_by_cycle[0][1]
    assert sum(value for _index, value in result.memory_by_cycle) == 100.0
    assert sum(value for _index, value in result.compute_by_cycle) == 200.0


def test_unverified_signal_cannot_receive_adaptive_bonus():
    result = create_adaptive_resource_allocation(
        (
            _metric(1, 1.0, False),
            _metric(2, 1.0, False),
        ),
        memory_capacity=100.0,
        compute_capacity=100.0,
        improvement_bonus=0.5,
    )

    assert result.memory_by_cycle == ((1, 50.0), (2, 50.0))
    assert result.compute_by_cycle == ((1, 50.0), (2, 50.0))


def test_adaptive_allocation_is_deterministic_and_bounded():
    metrics = (_metric(1, 0.0, True), _metric(2, 2.0, True))
    first = create_adaptive_resource_allocation(metrics, 64.0, 32.0)
    second = create_adaptive_resource_allocation(metrics, 64.0, 32.0)

    assert first == second
    assert sum(value for _index, value in first.memory_by_cycle) <= 64.0
    assert sum(value for _index, value in first.compute_by_cycle) <= 32.0
