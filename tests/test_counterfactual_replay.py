from src.counterfactual_replay import CounterfactualSpec, run_counterfactual
from src.recursive_convergence import run_recursive_convergence
from tests.test_recursive_convergence import _build


def _runner():
    population, initial, memory, compute = _build()

    def build(overrides=None):
        overrides = overrides or {}
        return run_recursive_convergence(
            population=population,
            initial_state=initial,
            proposal_builder=lambda index, state, previous: overrides.get(
                index,
                "observe initial state"
                if previous is None
                else f"refine from memory {previous.result.memory.id}",
            ),
            executor=lambda proposal: f"executed:{proposal.proposal}",
            quorum=2,
            new_singularity_builder=lambda index, proposal: f"counterfactual:{index}:{proposal.id}",
            created_at=(
                "2026-09-30T00:00:01Z",
                "2026-09-30T00:00:02Z",
                "2026-09-30T00:00:03Z",
            ),
            memory_resource=memory,
            compute_resource=compute,
            adaptive_memory_capacity=100.0,
            adaptive_compute_capacity=100.0,
            utility_builder=lambda index, previous: min(float(index) / 2.0, 1.0),
        )

    return build


def test_counterfactual_isolated_override_diverges_at_selected_cycle():
    build = _runner()
    baseline = build()
    spec = CounterfactualSpec(2, "counterfactual hypothesis")

    counterfactual, comparison = run_counterfactual(
        baseline=baseline,
        spec=spec,
        runner=build,
    )

    assert baseline.cycles[1].proposal.proposal != counterfactual.cycles[1].proposal.proposal
    assert comparison.cycle_index == 2
    assert comparison.baseline_proposal == "refine from memory " + baseline.cycles[0].result.memory.id
    assert comparison.counterfactual_proposal == "counterfactual hypothesis"
    assert comparison.diverged is True
    assert comparison.replay.first_divergence_cycle == 2
    assert comparison.replay.first_divergence_artifact == "proposal"
    assert all(
        item.match
        for item in comparison.replay.artifact_comparisons
        if item.cycle_index == 1
    )
    assert any(
        not item.match
        for item in comparison.replay.artifact_comparisons
        if item.cycle_index >= 2
    )


def test_counterfactual_same_input_preserves_baseline():
    build = _runner()
    baseline = build()
    spec = CounterfactualSpec(2, baseline.cycles[1].proposal.proposal)

    _, comparison = run_counterfactual(
        baseline=baseline,
        spec=spec,
        runner=build,
    )

    assert comparison.diverged is False
    assert comparison.replay.deterministic is True


def test_counterfactual_rejects_unknown_cycle():
    build = _runner()
    baseline = build()

    try:
        run_counterfactual(
            baseline=baseline,
            spec=CounterfactualSpec(4, "invalid"),
            runner=build,
        )
    except ValueError as exc:
        assert "existing baseline cycle" in str(exc)
    else:
        raise AssertionError("expected ValueError")
