from src.counterfactual_replay import CounterfactualSpec, run_counterfactual
from src.counterfactual_state_diff import build_counterfactual_state_diff
from src.counterfactual_impact_vector import build_counterfactual_impact_vector
from tests.test_counterfactual_replay import _runner


def test_impact_vector_is_deterministic_and_has_zero_baseline_for_identical_branch():
    build = _runner()
    baseline = build()
    counterfactual, comparison = run_counterfactual(
        baseline=baseline,
        spec=CounterfactualSpec(2, baseline.cycles[1].proposal.proposal),
        runner=build,
    )
    diff = build_counterfactual_state_diff(comparison, baseline, counterfactual)
    impact = build_counterfactual_impact_vector(comparison, baseline, counterfactual, diff)

    assert all(
        vector.delta_k == vector.delta_c == vector.delta_phi == vector.delta_utility == 0
        and vector.delta_omega_credit == 0
        and vector.changed_fields == 0
        for vector in impact.vectors
    )
    assert impact.aggregate.changed_fields == 0


def test_impact_vector_exposes_counterfactual_propagation():
    build = _runner()
    baseline = build()
    counterfactual, comparison = run_counterfactual(
        baseline=baseline,
        spec=CounterfactualSpec(2, "new hypothesis"),
        runner=build,
    )
    diff = build_counterfactual_state_diff(comparison, baseline, counterfactual)
    impact = build_counterfactual_impact_vector(comparison, baseline, counterfactual, diff)

    assert impact.first_divergence_cycle == 2
    assert impact.first_divergence_artifact == "proposal"
    assert impact.vectors[0].changed_fields == 0
    assert impact.vectors[1].changed_fields > 0
    assert impact.vectors[2].changed_fields > 0
