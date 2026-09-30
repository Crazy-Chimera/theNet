from src.causal_trace import build_causal_trace
from src.counterfactual_replay import CounterfactualSpec, run_counterfactual
from tests.test_counterfactual_replay import _runner


def test_causal_trace_exposes_modeled_downstream_dependency_chain():
    build = _runner()
    baseline = build()
    _, comparison = run_counterfactual(
        baseline=baseline,
        spec=CounterfactualSpec(2, "counterfactual hypothesis"),
        runner=build,
    )
    counterfactual = build({2: "counterfactual hypothesis"})

    trace = build_causal_trace(comparison, baseline, counterfactual)

    assert trace.first_divergence_cycle == 2
    assert trace.first_divergence_artifact == "proposal"
    assert trace.propagation_cycles == (2, 3)
    assert "C2:proposal" in trace.changed_artifacts
    assert "C2:outcome" in trace.changed_artifacts
    assert "C3:proposal" in trace.changed_artifacts
    assert any(step.relation == "informs_next_proposal" and step.changed for step in trace.steps)


def test_causal_trace_is_empty_for_identical_counterfactual():
    build = _runner()
    baseline = build()
    _, comparison = run_counterfactual(
        baseline=baseline,
        spec=CounterfactualSpec(2, baseline.cycles[1].proposal.proposal),
        runner=build,
    )
    counterfactual = build({2: baseline.cycles[1].proposal.proposal})

    trace = build_causal_trace(comparison, baseline, counterfactual)

    assert trace.first_divergence_cycle is None
    assert trace.steps == ()
    assert trace.propagation_cycles == ()
