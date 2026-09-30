from src.counterfactual_state_diff import build_counterfactual_state_diff
from src.counterfactual_replay import CounterfactualSpec, run_counterfactual
from tests.test_counterfactual_replay import _runner


def test_state_diff_reports_content_changes_and_numeric_deltas():
    build = _runner()
    baseline = build()
    counterfactual, comparison = run_counterfactual(
        baseline=baseline,
        spec=CounterfactualSpec(2, "counterfactual hypothesis"),
        runner=build,
    )

    diff = build_counterfactual_state_diff(comparison, baseline, counterfactual)

    assert diff.first_divergence_cycle == 2
    assert diff.first_divergence_artifact == "proposal"
    assert diff.changed_field_count > 0
    assert diff.propagation_cycles == (2, 3)
    metric_diffs = [
        item for item in diff.fields
        if item.scope == "metrics" and item.field == "k" and item.changed
    ]
    assert metric_diffs
    assert all(item.delta is not None for item in metric_diffs)


def test_state_diff_is_empty_for_identical_branch_content():
    build = _runner()
    baseline = build()
    _, comparison = run_counterfactual(
        baseline=baseline,
        spec=CounterfactualSpec(2, baseline.cycles[1].proposal.proposal),
        runner=build,
    )
    counterfactual = build({2: baseline.cycles[1].proposal.proposal})

    diff = build_counterfactual_state_diff(comparison, baseline, counterfactual)

    assert diff.changed_field_count == 0
    assert diff.propagation_cycles == ()
