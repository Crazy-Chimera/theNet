from src.counterfactual_experiment_matrix import (
    ExperimentCase,
    run_counterfactual_experiment_matrix,
)
from src.counterfactual_reproducibility import (
    compare_fingerprints,
    fingerprint_experiment_matrix,
)
from src.evidence_graph import build_evidence_graph
from tests.test_counterfactual_replay import _runner


def test_fingerprint_is_stable_and_case_order_independent():
    build = _runner()
    baseline = build()
    cases = (
        ExperimentCase("a", 2, "A"),
        ExperimentCase("b", 3, "B"),
    )
    matrix_a = run_counterfactual_experiment_matrix(
        baseline=baseline, cases=cases, runner=build
    )
    matrix_b = run_counterfactual_experiment_matrix(
        baseline=baseline, cases=tuple(reversed(cases)), runner=build
    )
    graph_id = build_evidence_graph(baseline).id
    fp_a = fingerprint_experiment_matrix(matrix_a, graph_id)
    fp_b = fingerprint_experiment_matrix(matrix_b, graph_id)

    assert fp_a.design_fingerprint == fp_b.design_fingerprint
    assert fp_a.result_fingerprint == fp_b.result_fingerprint


def test_identical_experiment_reproduces_exact_fingerprint():
    build = _runner()
    baseline_a = build()
    baseline_b = build()
    cases = (ExperimentCase("a", 2, "A"),)
    matrix_a = run_counterfactual_experiment_matrix(
        baseline=baseline_a, cases=cases, runner=build
    )
    matrix_b = run_counterfactual_experiment_matrix(
        baseline=baseline_b, cases=cases, runner=build
    )
    graph_a = build_evidence_graph(baseline_a).id
    graph_b = build_evidence_graph(baseline_b).id
    fp_a = fingerprint_experiment_matrix(matrix_a, graph_a)
    fp_b = fingerprint_experiment_matrix(matrix_b, graph_b)

    assert fp_a == fp_b
    assert compare_fingerprints(fp_a, fp_b)["reproducible"] is True


def test_changed_hypothesis_changes_design_fingerprint():
    build = _runner()
    baseline = build()
    graph_id = build_evidence_graph(baseline).id
    matrix_a = run_counterfactual_experiment_matrix(
        baseline=baseline,
        cases=(ExperimentCase("a", 2, "A"),),
        runner=build,
    )
    matrix_b = run_counterfactual_experiment_matrix(
        baseline=baseline,
        cases=(ExperimentCase("a", 2, "B"),),
        runner=build,
    )
    fp_a = fingerprint_experiment_matrix(matrix_a, graph_id)
    fp_b = fingerprint_experiment_matrix(matrix_b, graph_id)

    assert fp_a.design_fingerprint != fp_b.design_fingerprint
