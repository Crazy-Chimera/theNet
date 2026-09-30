from src.evidence_graph import build_evidence_graph
from src.replay import compare_recursive_replay
from tests.test_recursive_convergence import _build
from src.recursive_convergence import run_recursive_convergence


def _run():
    population, initial, memory, compute = _build()
    return run_recursive_convergence(
        population=population,
        initial_state=initial,
        proposal_builder=lambda index, state, previous: (
            "observe initial state"
            if previous is None
            else f"refine from memory {previous.result.memory.id}"
        ),
        executor=lambda proposal: f"executed:{proposal.proposal}",
        quorum=2,
        new_singularity_builder=lambda index, proposal: f"replay:{index}:{proposal.id}",
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


def test_replay_matches_immutable_recursive_artifacts():
    first = _run()
    second = _run()
    comparison = compare_recursive_replay(first, second)

    assert comparison.deterministic is True
    assert comparison.graph_match is True
    assert comparison.run_match is True
    assert comparison.artifact_match is True
    assert comparison.original_graph_id == build_evidence_graph(first).id


def test_replay_detects_changed_artifacts():
    first = _run()
    population, initial, memory, compute = _build()
    changed = run_recursive_convergence(
        population=population,
        initial_state=initial,
        proposal_builder=lambda index, state, previous: (
            "changed" if previous is None else f"refine:{previous.result.memory.id}"
        ),
        executor=lambda proposal: f"executed:{proposal.proposal}",
        quorum=2,
        new_singularity_builder=lambda index, proposal: f"replay:{index}:{proposal.id}",
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

    comparison = compare_recursive_replay(first, changed)
    assert comparison.deterministic is False
    assert comparison.graph_match is False
