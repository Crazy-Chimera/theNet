from src.counterfactual_experiment_matrix import (
    ExperimentCase,
    run_counterfactual_experiment_matrix,
)
from tests.test_counterfactual_replay import _runner


def test_experiment_matrix_uses_one_baseline_and_keeps_cases_independent():
    build = _runner()
    baseline = build()
    cases = (
        ExperimentCase("same", 2, baseline.cycles[1].proposal.proposal),
        ExperimentCase("hypothesis-a", 2, "alternative A"),
        ExperimentCase("hypothesis-b", 3, "alternative B"),
    )

    matrix = run_counterfactual_experiment_matrix(
        baseline=baseline,
        cases=cases,
        runner=build,
    )

    assert matrix.case_count == 3
    assert tuple(item.case.id for item in matrix.cases) == (
        "same", "hypothesis-a", "hypothesis-b"
    )
    assert matrix.cases[0].impact_vector.aggregate.changed_fields == 0
    assert matrix.cases[1].impact_vector.first_divergence_cycle == 2
    assert matrix.cases[2].impact_vector.first_divergence_cycle == 3


def test_experiment_matrix_rejects_duplicate_case_ids():
    build = _runner()
    baseline = build()
    cases = (
        ExperimentCase("duplicate", 2, "A"),
        ExperimentCase("duplicate", 3, "B"),
    )

    import pytest
    with pytest.raises(ValueError, match="unique"):
        run_counterfactual_experiment_matrix(
            baseline=baseline,
            cases=cases,
            runner=build,
        )
