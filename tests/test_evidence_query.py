from src.evidence_graph import build_evidence_graph
from src.evidence_query import query_evidence_graph, trace_evidence_path
from tests.test_recursive_convergence import _build


def test_evidence_graph_queries_are_bounded_and_deterministic():
    population, initial, memory, compute = _build()
    run = __import__("src.recursive_convergence", fromlist=["run_recursive_convergence"]).run_recursive_convergence(
        population=population,
        initial_state=initial,
        proposal_builder=lambda index, state, previous: (
            "observe" if previous is None else f"refine from memory {previous.result.memory.id}"
        ),
        executor=lambda proposal: f"executed:{proposal.proposal}",
        quorum=2,
        new_singularity_builder=lambda index, proposal: f"query:{index}:{proposal.id}",
        created_at=("2026-09-30T00:00:01Z", "2026-09-30T00:00:02Z", "2026-09-30T00:00:03Z"),
        memory_resource=memory,
        compute_resource=compute,
        utility_builder=lambda index, previous: min(float(index) / 2.0, 1.0),
    )
    graph = build_evidence_graph(run)
    proposal = run.cycles[1].proposal
    result = query_evidence_graph(graph, proposal.id, direction="backward", max_depth=2)
    assert result.node_id == proposal.id
    assert result.depth == 2
    assert any(edge.relation == "informs" for edge in result.edges)

    again = query_evidence_graph(graph, proposal.id, direction="backward", max_depth=2)
    assert result.as_dict() == again.as_dict()


def test_evidence_path_traces_proposal_to_memory():
    population, initial, memory, compute = _build()
    run = __import__("src.recursive_convergence", fromlist=["run_recursive_convergence"]).run_recursive_convergence(
        population=population,
        initial_state=initial,
        proposal_builder=lambda index, state, previous: (
            "observe" if previous is None else f"refine from memory {previous.result.memory.id}"
        ),
        executor=lambda proposal: f"executed:{proposal.proposal}",
        quorum=2,
        new_singularity_builder=lambda index, proposal: f"path:{index}:{proposal.id}",
        created_at=("2026-09-30T00:00:01Z", "2026-09-30T00:00:02Z", "2026-09-30T00:00:03Z"),
        memory_resource=memory,
        compute_resource=compute,
        utility_builder=lambda index, previous: min(float(index) / 2.0, 1.0),
    )
    graph = build_evidence_graph(run)
    path = trace_evidence_path(
        graph,
        run.cycles[1].proposal.id,
        run.cycles[1].result.memory.id,
        direction="forward",
    )
    assert path.depth == 5
    assert [edge.relation for edge in path.edges] == [
        "verified_by_consensus",
        "converges",
        "authorizes_execution",
        "produces",
        "remembered_as",
    ]
